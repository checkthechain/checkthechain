from ctc import rpc
from ctc import spec

from .. import uniswap_v3_spec


async def async_pool_slot0(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi('slot0', 'pool')
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )
    return {
        'sqrt_price_x96': result[0],
        'tick': result[1],
        'observation_index': result[2],
        'observation_cardinality': result[3],
        'observation_cardinality_next': result[4],
        'fee_protocol': result[5],
        'unlocked': result[6],
    }


async def async_pool_fee_growth_global_0_x128(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'feeGrowthGlobal0X128',
        'pool',
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_fee_growth_global_1_x128(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'feeGrowthGlobal1X128',
        'pool',
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_protocol_fees(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'protocolFees',
        'pool',
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_liquidity(
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'liquidity',
        'pool',
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )


async def async_pool_ticks(
    tick: int,
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi('ticks', 'pool')
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        function_parameters=[tick],
        provider=provider,
        block_number=block,
    )
    return {
        'liquidity_gross': result[0],
        'liquidity_net': result[1],
        'fee_growth_outside_0_x128': result[2],
        'fee_growth_outside_1_x128': result[3],
        'tick_cummulative_outside': result[4],
        'seconds_per_liquidity_outside_x128': result[5],
        'seconds_outside': result[6],
        'initialized': result[7],
    }


async def async_pool_tick_bitmap(
    word_position: int,
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'tickBitmap',
        'pool',
    )
    return await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
        function_parameters=[word_position],
    )


async def async_pool_positions(
    key: str,
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'positions',
        'pool',
    )
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        function_parameters=[key],
        provider=provider,
        block_number=block,
    )
    return {
        'liquidity': result[0],
        'fee_growth_inside_0_last_x128': result[1],
        'fee_growth_inside_1_last_x128': result[2],
        'tokens_owed_0': result[3],
        'tokens_owed_1': result[4],
    }


async def async_pool_observations(
    index: int,
    pool: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = None,
):
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'observations',
        'pool',
    )
    result = await rpc.async_eth_call(
        to_address=pool,
        function_abi=function_abi,
        function_parameters=[index],
        provider=provider,
        block_number=block,
    )
    return {
        'block_timestamp': result[0],
        'tick_cummulative': result[1],
        'seconds_per_liquidity_cummulative_x128': result[2],
        'initialized': result[3],
    }

