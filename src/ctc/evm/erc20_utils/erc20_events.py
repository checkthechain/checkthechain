import typing

from ctc import spec

from .. import block_utils
from .. import event_utils
from . import erc20_metadata
from . import erc20_abis


def get_token_amount_column(df):
    if 'arg__value' in df:
        return 'arg__value'
    elif 'arg__amount' in df:
        return 'arg__amount'
    elif 'arg__wad' in df:
        return 'arg__wad'
    else:
        raise Exception('could not detect amount column')


async def async_get_erc20_transfers(
    token_address: spec.ERC20Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    **event_kwargs
) -> spec.DataFrame:

    transfers = await event_utils.async_get_events(
        contract_address=token_address,
        event_abi=erc20_abis.erc20_event_abis['Transfer'],
        start_block=start_block,
        end_block=end_block,
        **event_kwargs
    )

    # detect amount column
    column = get_token_amount_column(df=transfers)
    transfers[column] = transfers[column].map(int)

    if normalize:

        # get block
        if start_block is not None:
            block = block_utils.standardize_block_number(start_block)
        elif end_block != 'latest' and end_block is not None:
            block = block_utils.standardize_block_number(end_block)
        else:
            block = await block_utils.async_get_latest_block_number()

        decimals = await erc20_metadata.async_get_erc20_decimals(
            token=token_address, block=block
        )
        dtype = float
        transfers[column] = transfers[column] / dtype('1e' + str(decimals))

    return transfers


async def async_get_erc20_holdings_from_transfers(
    transfers: spec.DataFrame,
    block: typing.Optional[spec.BlockNumberReference] = None,
    dtype: typing.Optional[
        typing.Union[typing.Type[int], typing.Type[float]]
    ] = None,
    normalize: bool = False,
) -> spec.DataFrame:

    # filter block
    if block is not None:
        blocks = transfers.index.get_level_values('block_number').values
        mask = blocks <= block
        transfers = transfers[mask]

    amount_key = get_token_amount_column(transfers)

    # convert to float
    if dtype is not None:
        transfers[amount_key] = transfers[amount_key].map(dtype)

    # subtract transfers out from transfers in
    from_transfers = transfers.groupby('arg__from')[amount_key].sum()
    to_transfers = transfers.groupby('arg__to')[amount_key].sum()
    balances = to_transfers.sub(from_transfers, fill_value=0)

    if normalize:
        decimals = await erc20_metadata.async_get_erc20_decimals(
            transfers['contract_address'].values[0]
        )
        balances /= 10 ** decimals

    # sort
    balances = balances.sort_values(ascending=False)

    balances.name = 'balance'
    balances.index.name = 'address'

    return balances

