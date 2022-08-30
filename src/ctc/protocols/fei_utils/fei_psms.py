from __future__ import annotations

import time
import typing

import tooltime
import toolstr

from ctc import evm
from ctc import spec


address_psms = {
    '0x2a188f9eb761f70ecea083ba6c2a40145078dfc2': 'DAI PSM',
    '0xb0e731f036adfdec12da77c15aab0f90e8e45a0e': 'LUSD PSM',
    '0x5dde9b4b14edf59cb23c1d4579b279846998205e': 'RAI PSM',
    '0x98e5f5706897074a4664dd3a32eb80242d6e694b': 'ETH PSM',
}


psm_colors = {
    'ETH PSM': 'mediumslateblue',
    'RAI PSM': 'mediumspringgreen',
    'DAI PSM': 'orange',
    'LUSD PSM': 'dodgerblue',
    'Old DAI PSM': 'grey',
}


def get_psms(
    start_block: spec.BlockNumberReference | None = None,
) -> typing.Mapping[str, spec.Address]:
    psms = {v: k for k, v in address_psms.items()}
    if isinstance(start_block, int) and start_block < 14098619:
        psms['Old DAI PSM'] = '0x210300c158f95e1342fd008ae417ef68311c49c2'
    return psms


async def async_get_fei_psm_mints(
    *,
    start_block: spec.BlockNumberReference = 14000000,
    end_block: spec.BlockNumberReference = 'latest',
    psms: typing.Mapping[str, spec.Address] | None = None,
    timestamp: bool = True,
    normalize: bool = True,
    include_price: bool = True,
) -> spec.DataFrame:

    import asyncio
    import pandas as pd

    if psms is None:
        psms = get_psms()

    coroutines = []
    for psm_name, psm_address in psms.items():
        coroutine = evm.async_get_events(
            contract_address=psm_address,
            event_name='Mint',
            start_block=start_block,
            end_block=end_block,
            verbose=False,
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    psm_mints = dict(zip(psms.keys(), results))
    for psm in psm_mints.keys():
        psm_mints[psm].index = psm_mints[psm].index.get_level_values(
            'block_number'
        )
        psm_mints[psm]['token'] = psm[:-4]

    if typing.TYPE_CHECKING:
        mints = typing.cast(spec.DataFrame, pd.concat(list(psm_mints.values())))
    else:
        mints = pd.concat(list(psm_mints.values()))
    mints = mints.sort_index()

    # add extra fields
    redeem_blocks = mints.index.values
    if timestamp:
        mints['timestamp'] = await evm.async_get_block_timestamps(redeem_blocks)
    if normalize:
        mints['arg__amountFeiOut'] = (
            mints['arg__amountFeiOut'].map(int) / 1e18
        ).astype(float)
        mints['arg__amountIn'] = mints['arg__amountIn'].astype(float)

    if include_price:
        if not normalize:
            raise Exception('must normalize to compute price')
        mints['fei_per_token'] = (
            mints['arg__amountFeiOut'] / mints['arg__amountIn'] * 1e18
        )
        mints['token_per_fei'] = 1 / mints['fei_per_token']

    return mints


async def async_get_fei_psm_redemptions(
    *,
    start_block: spec.BlockNumberReference = 14000000,
    end_block: spec.BlockNumberReference = 'latest',
    psms: typing.Mapping[str, spec.Address] | None = None,
    timestamp: bool = True,
    normalize: bool = True,
    include_price: bool = True,
) -> spec.DataFrame:
    import asyncio
    import pandas as pd

    if psms is None:
        psms = get_psms()

    coroutines = []
    for psm_name, psm_address in psms.items():
        coroutine = evm.async_get_events(
            contract_address=psm_address,
            event_name='Redeem',
            start_block=start_block,
            end_block=end_block,
            verbose=False,
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    psm_redeems = dict(zip(psms.keys(), results))
    for psm in psm_redeems.keys():
        psm_redeems[psm].index = psm_redeems[psm].index.get_level_values(
            'block_number'
        )
        psm_redeems[psm]['token'] = psm[:-4]

    data = pd.concat(list(psm_redeems.values()))
    if typing.TYPE_CHECKING:
        redemptions = typing.cast(spec.DataFrame, data)
    else:
        redemptions = data
    redemptions = redemptions.sort_index()

    # add extra fields
    redeem_blocks = redemptions.index.values
    if timestamp:
        redemptions['timestamp'] = await evm.async_get_block_timestamps(
            redeem_blocks
        )
    if normalize:
        redemptions['arg__amountFeiIn'] = (
            redemptions['arg__amountFeiIn'].map(int) / 1e18
        ).astype(float)
        redemptions['arg__amountAssetOut'] = redemptions[
            'arg__amountAssetOut'
        ].astype(float)

    if include_price:
        if not normalize:
            raise Exception('must normalize to compute price')
        redemptions['fei_per_token'] = (
            redemptions['arg__amountFeiIn']
            / redemptions['arg__amountAssetOut']
            * 1e18
        )
        redemptions['token_per_fei'] = 1 / redemptions['fei_per_token']

    return redemptions


def print_fei_psm_mints(
    mints: spec.DataFrame, *, limit: int = 30, verbose: bool = False
) -> None:

    labels = [
        'block',
        'age',
        'token',
        'FEI',
        'total',
    ]
    if verbose:
        labels.append('hash')

    mints = mints.iloc[-limit:].copy()
    mints['cummulative'] = mints['arg__amountFeiOut'].cumsum()
    now = int(time.time())
    rows = []
    for block, mint in mints.iterrows():
        age = now - mint['timestamp']
        age_str = tooltime.timelength_to_phrase(age)
        age_str = ' '.join(age_str.split(' ')[:4])
        age_str = age_str.rstrip(',')

        row = [
            #         tooltime.convert_timestamp(row['timestamp'], 'TimestampISOPretty'),
            str(block),
            age_str,
            mint['token'],
            mint['arg__amountFeiOut'],
            mint['cummulative'],
        ]

        if verbose:
            row.append(mint['transaction_hash'])

        rows.append(row)

    toolstr.print_text_box('Recent Mints')
    print()
    format = {
        'order_of_magnitude': True,
        'trailing_zeros': True,
        'oom_blank': ' ',
    }
    toolstr.print_table(rows, labels=labels, format=format)


def print_fei_psm_redemptions(
    redemptions: spec.DataFrame,
    *,
    limit: int = 30,
    verbose: bool = False,
) -> None:

    labels = [
        'block',
        'age',
        'token',
        'FEI',
        'total',
    ]
    if verbose:
        labels.append('hash')

    redemptions = redemptions.iloc[-limit:].copy()
    redemptions['cummulative'] = redemptions['arg__amountFeiIn'].cumsum()
    now = int(time.time())
    rows = []
    for block, redeem in redemptions.iterrows():
        age = now - redeem['timestamp']
        age_str = tooltime.timelength_to_phrase(age)
        age_str = ' '.join(age_str.split(' ')[:4])
        age_str = age_str.rstrip(',')

        row = [
            #         tooltime.convert_timestamp(row['timestamp'], 'TimestampISOPretty'),
            str(block),
            age_str,
            redeem['token'],
            redeem['arg__amountFeiIn'],
            redeem['cummulative'],
        ]

        if verbose:
            row.append(redeem['transaction_hash'])

        rows.append(row)

    toolstr.print_text_box('Recent Redeems')
    print()
    format = {
        'order_of_magnitude': True,
        'trailing_zeros': True,
        'oom_blank': ' ',
    }
    toolstr.print_table(rows, labels=labels, format=format)
