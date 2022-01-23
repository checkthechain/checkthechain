from ctc import rpc

from .. import rari_abis


async def async_get_irm_blocks_per_year(interest_rate_model, block='latest'):

    try:
        return await rpc.async_eth_call(
            to_address=interest_rate_model,
            block_number=block,
            function_abi=rari_abis.interest_rate_model_abis['blocksPerYear'],
        )
    except KeyError:
        return await rpc.async_eth_call(
            to_address=rari_abis.contract_examples['InterestRateModel'],
            block_number=block,
            function_abi=rari_abis.interest_rate_model_abis['blocksPerYear'],
        )


