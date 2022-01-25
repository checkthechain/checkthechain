import asyncio

from ctc import evm
from ctc import rpc
from ctc import spec


#
# # metadata
#


async def download_pool_abi(pool_address):
    example_pool = '0x8f8ef111b67c04eb1641f5ff19ee54cda062f163'
    await evm.async_save_proxy_contract_abi_to_filesystem(
        contract_address=pool_address,
        proxy_implementation=example_pool,
    )


async def ensure_pool_abi(pool_address):
    try:
        await evm.async_get_contract_abi(contract_address=pool_address)
    except spec.AbiNotFoundException:
        await download_pool_abi(pool_address)


async def async_get_pool_tokens(pool_address, **rpc_kwargs):
    kwargs = dict(rpc_kwargs, to_address=pool_address)
    return await asyncio.gather(
        rpc.async_eth_call(function_name='token0', **kwargs),
        rpc.async_eth_call(function_name='token1', **kwargs),
    )


async def async_get_pool_metadata(pool_address, **rpc_kwargs):
    await ensure_pool_abi(pool_address)

    x_address, y_address = await async_get_pool_tokens(
        pool_address=pool_address
    )
    x_symbol, y_symbol = await evm.async_get_erc20s_symbols(
        tokens=[x_address, y_address], **rpc_kwargs
    )
    return {
        'x_symbol': x_symbol,
        'y_symbol': y_symbol,
        'x_address': x_address,
        'y_address': y_address,
    }


#
# # events
#


async def async_get_pool_swaps(
    pool_address,
    start_block=None,
    end_block=None,
    replace_symbols=False,
    normalize=True,
):
    await ensure_pool_abi(pool_address)

    if normalize or replace_symbols:
        metadata_task = asyncio.create_task(
            async_get_pool_metadata(pool_address)
        )

    swaps = await evm.async_get_events(
        event_name='Swap',
        contract_address=pool_address,
        start_block=start_block,
        end_block=end_block,
    )

    if normalize or replace_symbols:
        metadata = await metadata_task

    # rename columns
    if replace_symbols:
        x_symbol = metadata['x_symbol']
        y_symbol = metadata['y_symbol']
    else:
        x_symbol = 'x'
        y_symbol = 'y'
    columns = {
        'arg__amount0': x_symbol + '_amount',
        'arg__amount1': y_symbol + '_amount',
    }
    swaps = swaps.rename(columns=columns)

    # normalize columns
    if normalize:
        x_decimals, y_decimals = await evm.async_get_erc20s_decimals(
            tokens=[metadata['x_address'], metadata['y_address']],
        )
        swaps[columns['arg__amount0']] = swaps[columns['arg__amount0']].astype(
            float
        ) / (10 ** x_decimals)
        swaps[columns['arg__amount1']] = swaps[columns['arg__amount1']].astype(
            float
        ) / (10 ** y_decimals)

    return swaps

