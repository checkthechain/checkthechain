from __future__ import annotations

from ctc import spec


async def async_get_irm_blocks_per_year(
    interest_rate_model: spec.Address,
    block: spec.BlockNumberReference = 'latest',
) -> int:

    return 2102400
    # try:
    #     return await rpc.async_eth_call(
    #         to_address=interest_rate_model,
    #         block_number=block,
    #         function_abi=rari_abis.interest_rate_model_abis['blocksPerYear'],
    #     )
    # except KeyError:
    #     return await rpc.async_eth_call(
    #         to_address=rari_abis.contract_examples['InterestRateModel'],
    #         block_number=block,
    #         function_abi=rari_abis.interest_rate_model_abis['blocksPerYear'],
    #     )
