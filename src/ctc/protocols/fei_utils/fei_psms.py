from __future__ import annotations

import asyncio
import time

import pandas as pd
import tooltime
import tooltable
import toolstr

from ctc import evm


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


def get_psms(start_block=None):
    psms = {v: k for k, v in address_psms.items()}
    if start_block is not None and start_block < 14098619:
        psms['Old DAI PSM'] = '0x210300c158f95e1342fd008ae417ef68311c49c2'
    return psms


async def async_get_fei_psm_mints(
    start_block=14000000,
    end_block='latest',
    psms=None,
    timestamp=True,
    normalize=True,
):
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

    mints = pd.concat(psm_mints.values())
    mints = mints.sort_index()

    # add extra fields
    redeem_blocks = mints.index.values
    if timestamp:
        mints['timestamp'] = await evm.async_get_block_timestamps(
            redeem_blocks
        )
    if normalize:
        mints['arg__amountFeiOut'] = (
            mints['arg__amountFeiOut'].map(int) / 1e18
        )

    return mints


async def async_get_fei_psm_redemptions(
    start_block=14000000,
    end_block='latest',
    psms=None,
    timestamp=True,
    normalize=True,
    cummulative=True,
):
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

    redemptions = pd.concat(psm_redeems.values())
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
        )

    return redemptions


def print_fei_psm_mints(mints, limit=30):

    headers = [
        'block',
        'age',
        'token',
        'FEI',
        'total',
    ]

    mints = mints.iloc[-limit:].copy()
    mints['cummulative'] = mints['arg__amountFeiOut'].cumsum()
    now = int(time.time())
    rows = []
    for block, row in mints.iterrows():
        age = now - row['timestamp']
        age_str = tooltime.timelength_to_phrase(age)
        age_str = ' '.join(age_str.split(' ')[:4])
        age_str = age_str.rstrip(',')

        row = [
            #         tooltime.convert_timestamp(row['timestamp'], 'TimestampISOPretty'),
            str(block),
            age_str,
            row['token'],
            toolstr.format(row['arg__amountFeiOut'], order_of_magnitude=True),
            toolstr.format(row['cummulative'], order_of_magnitude=True),
        ]
        rows.append(row)

    toolstr.print_text_box('Recent Mints')
    print()
    tooltable.print_table(rows, headers=headers)


def print_fei_psm_redemptions(redemptions, limit=30):

    headers = [
        'block',
        'age',
        'token',
        'FEI',
        'total',
    ]

    redemptions = redemptions.iloc[-limit:].copy()
    redemptions['cummulative'] = redemptions['arg__amountFeiIn'].cumsum()
    now = int(time.time())
    rows = []
    for block, row in redemptions.iterrows():
        age = now - row['timestamp']
        age_str = tooltime.timelength_to_phrase(age)
        age_str = ' '.join(age_str.split(' ')[:4])
        age_str = age_str.rstrip(',')

        row = [
            #         tooltime.convert_timestamp(row['timestamp'], 'TimestampISOPretty'),
            str(block),
            age_str,
            row['token'],
            toolstr.format(row['arg__amountFeiIn'], order_of_magnitude=True),
            toolstr.format(row['cummulative'], order_of_magnitude=True),
        ]
        rows.append(row)

    toolstr.print_text_box('Recent Redeems')
    print()
    tooltable.print_table(rows, headers=headers)
