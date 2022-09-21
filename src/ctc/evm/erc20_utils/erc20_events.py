from __future__ import annotations

import typing

from ctc import spec

from .. import abi_utils
from .. import event_utils
from . import erc20_metadata
from . import erc20_spec

if typing.TYPE_CHECKING:
    import tooltime


def _get_token_amount_column(df: spec.DataFrame) -> str:
    if 'arg__amount' in df:
        return 'arg__amount'
    elif 'arg__value' in df:
        return 'arg__value'
    elif 'arg__wad' in df:
        return 'arg__wad'
    else:
        raise Exception('could not detect amount column')


async def async_get_erc20_transfers(
    token: spec.ERC20Reference,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    normalize: bool = True,
    convert_from_str: bool = True,
    verbose: bool = False,
    provider: spec.ProviderReference = None,
    **event_kwargs: typing.Any,
) -> spec.DataFrame:
    """get transfer events of ERC20 token"""

    from ctc import rpc

    network = rpc.get_provider_network(provider)
    token_address = await erc20_metadata.async_get_erc20_address(
        token, network=network
    )

    # use token's own abi if available, otherwise fallback to standard
    # do this because tokens sometimes have different values for event args
    try:
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=token, event_name='Transfer'
        )
    except Exception:
        event_abi = erc20_spec.erc20_event_abis['Transfer']

    transfers = await event_utils.async_get_events(
        contract_address=token_address,
        event_abi=event_abi,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
        verbose=verbose,
        provider=provider,
        **event_kwargs,
    )

    # make amount column name the same across all tokens
    old_column = 'arg__' + event_abi['inputs'][2]['name']
    column = 'arg__amount'
    transfers = transfers.rename(columns={old_column: column})

    # convert from str amounts to int amounts
    if convert_from_str:
        transfers[column] = transfers[column].map(int)

    # normalize
    if normalize and len(transfers) > 0:

        if not convert_from_str:
            raise Exception(
                'cannot normalize without str conversion'
                ', use normalize=False or convert_from_str=True'
            )

        decimals = await erc20_metadata.async_get_erc20_decimals(
            token=token_address,
            block=transfers.index.values[0][0],
        )
        dtype = float
        transfers[column] = transfers[column] / dtype('1e' + str(decimals))

    else:

        # prevent implicit conversion to int64
        # - this happens to ERC20's that use small number of decimals
        # - keep all quantities as native python ints for consistency
        if transfers[column].dtype.name != 'object':
            transfers[column] = transfers[column].astype(object)

    return transfers


async def async_get_erc20_balances_from_transfers(
    transfers: spec.DataFrame,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    dtype: typing.Optional[
        typing.Union[typing.Type[int], typing.Type[float]]
    ] = None,
    normalize: bool = False,
) -> spec.DataFrame:
    """compute ERC20 balance of each wallet using Transfer events"""

    # filter block
    if block is not None:
        blocks = transfers.index.get_level_values('block_number').values
        mask = blocks <= block
        transfers = transfers[mask]

    amount_key = _get_token_amount_column(transfers)

    # convert to float
    if dtype is not None:
        transfers[amount_key] = transfers[amount_key].map(dtype)

    # subtract transfers out from transfers in
    from_transfers = transfers.groupby('arg__from')[amount_key].sum()
    to_transfers = transfers.groupby('arg__to')[amount_key].sum()
    balances: spec.DataFrame = to_transfers.sub(from_transfers, fill_value=0)

    if normalize:
        decimals = await erc20_metadata.async_get_erc20_decimals(
            transfers['contract_address'].values[0]
        )
        balances /= 10 ** decimals

    # sort
    balances = balances.sort_values(ascending=False)  # type: ignore

    balances.name = 'balance'
    balances.index.name = 'address'

    return balances
