import typing

from ctc import spec

from .. import block_utils
from .. import event_utils
from . import erc20_metadata


# import pandas


async def async_get_erc20_transfers(
    token_address: spec.ERC20Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: spec.BlockNumberReference = 'latest',
    normalize: bool = True,
    **event_kwargs
) -> spec.DataFrame:

    transfers = await event_utils.async_get_events(
        contract_address=token_address,
        event_name='Transfer',
        start_block=start_block,
        end_block=end_block,
        **event_kwargs
    )

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
        transfers['arg__value'] = transfers['arg__value'] / dtype(
            '1e' + str(decimals)
        )

    return transfers


async def async_get_erc20_balances_from_transfers(
    transfers: spec.DataFrame,
    block: typing.Optional[spec.BlockNumberReference] = None,
    dtype: typing.Union[typing.Type[int], typing.Type[float]] = float,
    # normalize: bool = True,
) -> spec.DataFrame:

    # filter block
    if block is not None:
        blocks = transfers.index.get_level_values('block_number').values
        mask = blocks <= block
        transfers = transfers[mask]

    if 'arg__amount' in transfers.columns:
        amount_key = 'arg__amount'
    elif 'arg__value' in transfers.columns:
        amount_key = 'arg__value'
    else:
        raise Exception('could not detect a transfer amout key in transfers')

    # convert to float
    transfers[amount_key] = transfers[amount_key].map(dtype)

    # subtract transfers out from transfers in
    from_transfers = transfers.groupby('arg__from')[amount_key].sum()
    to_transfers = transfers.groupby('arg__to')[amount_key].sum()
    balances = to_transfers.sub(from_transfers, fill_value=0)

    # # normalize
    # if normalize:
    #     block = transfers.index[-1][0]
    #     if block is None:
    #         raise Exception('could not determine any valid block')
    #     address = transfers['contract_address'].iloc[0]
    #     decimals = await erc20_metadata.async_get_erc20_decimals(
    #         token=address, block=block
    #     )
    #     balances = balances / dtype('1e' + str(decimals))

    # sort
    balances = balances.sort_values(ascending=False)

    balances.name = 'transfer_amount'

    return balances

