import asyncio
import math

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc.protocols import chainlink_utils

from . import rari_abis


fuse_directory = '0x835482fe0532f169024d5e9410199369aad5c77e'


async def async_get_all_pools(block='latest'):
    return await rpc.async_eth_call(
        to_address=fuse_directory,
        function_name='getAllPools',
        block_number=block,
    )


#
# # comptroller functions
#


async def save_comptroller_proxy_implementation(comptroller, block='latest'):
    implementation = await rpc.async_eth_call(
        to_address=comptroller,
        function_name='comptrollerImplementation',
        block_number=block,
    )
    evm.save_proxy_contract_abi_to_filesystem(comptroller, implementation)


async def async_get_pool_ctoken(comptroller, underlying, block='latest'):
    return await rpc.async_eth_call(
        to_address=comptroller,
        function_name='cTokensByUnderlying',
        function_parameters=[underlying],
        block_number=block,
    )


async def async_get_pool_ctokens(comptroller, block='latest'):
    return await rpc.async_eth_call(
        to_address=comptroller,
        function_name='getAllMarkets',
        block_number=block,
    )


async def async_get_pool_oracle(comptroller, block='latest'):
    return await rpc.async_eth_call(
        to_address=comptroller,
        function_name='oracle',
        block_number=block,
    )


async def async_get_pool_name(comptroller, all_pools=None, block='latest'):
    comptroller = comptroller.lower()
    if all_pools is None:
        all_pools = await async_get_all_pools(block=block)
    for pool in all_pools:
        if pool[2] == comptroller:
            return pool[0]
    else:
        raise Exception('could not find pool')


async def async_get_pool_prices(
    *,
    oracle=None,
    ctokens=None,
    comptroller=None,
    block='latest',
    to_usd=True,
):
    if oracle is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        oracle = await async_get_pool_oracle(comptroller, block=block)
    if ctokens is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        ctokens = await async_get_pool_ctokens(comptroller, block=block)

    coroutines = [
        async_get_ctoken_price(ctoken=ctoken, oracle=oracle, block=block)
        for ctoken in ctokens
    ]
    prices = await asyncio.gather(*coroutines)

    if to_usd:
        eth_price = chainlink_utils.fetch_eth_price(block=block)
        prices = [price * eth_price for price in prices]

    return dict(zip(ctokens, prices))


async def async_get_pool_tokens(
    *, ctokens=None, comptroller=None, block='latest'
):
    if ctokens is None:
        if comptroller is None:
            raise Exception('specify comptroller')
        ctokens = await async_get_pool_ctokens(comptroller, block=block)

    coroutines = [
        async_get_ctoken_underlying(ctoken=ctoken) for ctoken in ctokens
    ]
    underlyings = await asyncio.gather(*coroutines)
    return dict(zip(ctokens, underlyings))


async def get_pool_tvl_and_tvb(
    *, comptroller=None, ctokens=None, oracle=None, block='latest'
):
    if ctokens is None:
        if comptroller is None:
            raise Exception(
                'must specify comptroller if not specifying ctokens'
            )
        ctokens = await async_get_pool_ctokens(
            comptroller=comptroller, block=block
        )
    if oracle is None:
        if comptroller is None:
            raise Exception('must specify comptroller if not specifying oracle')
        oracle = await async_get_pool_oracle(
            comptroller=comptroller, block=block
        )

    eth_price = chainlink_utils.fetch_eth_price(block=block)

    ctokens_stats = [
        asyncio.create_task(
            async_get_ctoken_tvl_and_tvb(ctoken, oracle, eth_price, block=block)
        )
        for ctoken in ctokens
    ]
    ctokens_stats = await asyncio.gather(*ctokens_stats)

    tvl = 0
    tvb = 0
    for ctoken_stats in ctokens_stats:
        tvl += ctoken_stats['tvl']
        tvb += ctoken_stats['tvb']

    return {'tvl': tvl, 'tvb': tvb}


async def async_get_ctoken_tvl_and_tvb(
    ctoken, oracle, eth_price, block='latest'
):

    # send queries
    borrowed = asyncio.create_task(
        async_get_total_borrowed(ctoken=ctoken, block=block)
    )
    liquidity = asyncio.create_task(
        async_get_total_liquidity(ctoken=ctoken, block=block)
    )
    price = asyncio.create_task(
        async_get_ctoken_price(ctoken=ctoken, oracle=oracle, block=block)
    )

    # receive results
    borrowed = await borrowed
    borrowed /= 1e18
    liquidity = await liquidity
    liquidity /= 1e18
    price = await price

    # compute output
    return {
        'tvb': borrowed * price * eth_price,
        'tvl': (borrowed + liquidity) * price * eth_price,
    }


#
# # interest rate model functions
#


async def async_get_blocks_per_year(interest_rate_model, block='latest'):
    return await rpc.async_eth_call(
        to_address=interest_rate_model,
        function_name='blocksPerYear',
        block_number=block,
        function_abi=rari_abis.interest_rate_model_function_abis['blocksPerYear'],
    )


#
# # ctoken functions
#


async def async_get_ctoken_price(
    ctoken, oracle, block='latest', normalize=True
):
    price = await rpc.async_eth_call(
        to_address=oracle,
        function_name='getUnderlyingPrice',
        function_parameters=[ctoken],
        block_number=block,
    )
    if normalize:
        price /= 1e18
    return price


async def async_get_ctoken_comptroller(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_name='comptroller',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['comptroller'],
    )


async def async_get_ctoken_underlying(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_name='underlying',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['underlying'],
    )


async def async_get_interest_rate_model(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_name='interestRateModel',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['interestRateModel'],
    )


async def async_get_total_borrowed(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_name='totalBorrows',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['totalBorrows'],
    )


async def async_get_total_liquidity(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_name='getCash',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['getCash'],
    )


async def async_get_reserves(ctoken, block='latest'):
    return await rpc.async_eth_call(
        to_address=ctoken,
        function_name='totalReserves',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['totalReserves'],
    )


async def async_get_supply_interest_per_block(
    ctoken, block='latest', normalize=True
):
    result = await rpc.async_eth_call(
        to_address=ctoken,
        function_name='supplyRatePerBlock',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['supplyRatePerBlock'],
    )
    if normalize:
        result /= 1e18
    return result


async def async_get_borrow_interest_per_block(
    ctoken, block='latest', normalize=True
):
    result = await rpc.async_eth_call(
        to_address=ctoken,
        function_name='borrowRatePerBlock',
        block_number=block,
        function_abi=rari_abis.ctoken_function_abis['borrowRatePerBlock'],
    )
    if normalize:
        result /= 1e18
    return result


async def async_get_supply_apy(ctoken, blocks_per_year=None, block='latest'):
    supply_interest_per_block = await async_get_supply_interest_per_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
    )
    if blocks_per_year is None:
        blocks_per_year = None
    return (1 + supply_interest_per_block) ** blocks_per_year - 1


async def async_get_borrow_apy(ctoken, blocks_per_year=None, block='latest'):
    borrow_interest_per_block = await async_get_borrow_interest_per_block(
        ctoken=ctoken,
        block=block,
        normalize=True,
    )
    if blocks_per_year is None:
        blocks_per_year = None
    return (1 + borrow_interest_per_block) ** blocks_per_year - 1


#
# # aggregation
#


async def async_get_pool_summary_data(comptroller, block='latest'):

    # get block number
    if block == 'latest':
        block = await rpc.async_eth_block_number()

    # get pool data
    ctokens = await async_get_pool_ctokens(comptroller, block=block)
    underlyings = await async_get_pool_tokens(ctokens=ctokens, block=block)
    token_names = []
    for underlying in underlyings.values():
        if underlying == '0x0000000000000000000000000000000000000000':
            token_name = 'ETH'
        elif underlying in directory.address_to_symbol:
            token_name = directory.address_to_symbol[underlying]
        else:
            token_name = evm.get_erc20_symbol(underlying)
        token_names.append(token_name)

    # get pricing data
    token_prices = await async_get_pool_prices(
        ctokens=ctokens, comptroller=comptroller, block=block
    )

    tokens_data = {}
    blocks_per_year = None
    for ctoken, underlying, token_name in zip(
        ctokens, underlyings, token_names
    ):

        # get blocks per year
        if blocks_per_year is None:
            interest_rate_model = await async_get_interest_rate_model(
                ctoken=ctoken,
                block=block,
            )
            blocks_per_year = await async_get_blocks_per_year(
                interest_rate_model=interest_rate_model,
                block=block,
            )

        # get ctoken stats
        borrowed = await async_get_total_borrowed(ctoken=ctoken, block=block)
        borrowed /= 1e18
        liquidity = await async_get_total_liquidity(ctoken=ctoken, block=block)
        liquidity /= 1e18
        supply_apy = await async_get_supply_apy(
            ctoken=ctoken,
            block=block,
            blocks_per_year=blocks_per_year,
        )
        borrow_apy = await async_get_borrow_apy(
            ctoken=ctoken,
            block=block,
            blocks_per_year=blocks_per_year,
        )

        # compute derived stats
        supplied = borrowed + liquidity
        if math.isclose(supplied, 0):
            utilization = 0
        else:
            utilization = borrowed / supplied

        tokens_data[token_name] = {
            'name': token_name,
            'borrowed': borrowed,
            'borrowed_tvl': borrowed * token_prices[ctoken],
            'supplied': supplied,
            'supplied_tvl': supplied * token_prices[ctoken],
            'liquidity': liquidity,
            'liquidity_tvl': liquidity * token_prices[ctoken],
            'utilization': utilization,
            'borrow_apy': borrow_apy,
            'supply_apy': supply_apy,
        }

    return tokens_data

