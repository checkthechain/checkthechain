from __future__ import annotations

import typing

from ctc import spec

from .. import abi_utils
from .. import event_utils
from . import erc20_metadata
from . import erc20_spec

if typing.TYPE_CHECKING:
    import tooltime


def _get_token_amount_column(df: spec.PolarsDataFrame) -> str:
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
    verbose: bool = False,
    context: spec.Context = None,
    **event_kwargs: typing.Any,
) -> spec.PolarsDataFrame:
    """get transfer events of ERC20 token"""

    token_address = await erc20_metadata.async_get_erc20_address(
        token, context=context
    )

    # use token's own abi if available, otherwise fallback to standard
    # do this because tokens sometimes have different values for event args
    try:
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=token,
            event_name='Transfer',
            context=context,
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
        context=context,
        **event_kwargs,
    )

    # make amount column name the same across all tokens
    old_column = 'arg__' + event_abi['inputs'][2]['name']
    column = 'arg__amount'
    transfers = transfers.rename({old_column: column})

    # normalize
    if normalize and len(transfers) > 0:

        import polars as pl
        import numpy as np

        decimals = await erc20_metadata.async_get_erc20_decimals(
            token=token_address,
            block=transfers['block_number'][0],
            context=context,
        )
        factor = float('1e' + str(decimals))
        normalized = np.array(transfers[column].to_list(), dtype=float) / factor
        transfers = transfers.with_columns(pl.Series(column, normalized))

    return transfers


async def async_get_erc20_balances_from_transfers(
    transfers: spec.PolarsDataFrame,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    normalize: bool = False,
    context: spec.Context = None,
) -> spec.PolarsDataFrame:
    """compute ERC20 balance of each wallet using Transfer events"""

    import polars as pl

    # filter block
    if block is not None:
        transfers = transfers.filter(pl.col('block_number') <= block)

    amount_key = _get_token_amount_column(transfers)

    # subtract transfers out from transfers in
    from_transfers = transfers.groupby('arg__from').agg(pl.sum(amount_key))
    to_transfers = transfers.groupby('arg__to').agg(pl.sum(amount_key))
    balances: spec.PolarsDataFrame = to_transfers.sub(from_transfers, fill_value=0)  # type: ignore

    if normalize:
        decimals = await erc20_metadata.async_get_erc20_decimals(
            typing.cast(str, transfers['contract_address'].values[0]),
            context=context,
        )
        balances /= 10**decimals

    # sort
    balances = balances.sort_values(ascending=False)  # type: ignore

    balances.name = 'balance'
    balances.index.name = 'address'

    return balances

