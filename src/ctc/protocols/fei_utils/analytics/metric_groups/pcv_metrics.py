import asyncio

from ctc import evm
from ctc.protocols import fei_utils
from .. import spec


async def async_compute_pcv_stats(
    blocks: list[int],
    verbose: bool = False,
) -> dict[spec.MetricGroupName, spec.MetricGroup]:

    pcv_stats_task = asyncio.create_task(
        fei_utils.async_get_pcv_stats(blocks=blocks)
    )
    total_supply_task = asyncio.create_task(
        evm.async_get_erc20_total_supply(token='FEI', blocks=blocks)
    )

    pcv_stats = await pcv_stats_task

    user_fei = pcv_stats['user_fei']
    pcv_total = pcv_stats['pcv']
    cr = pcv_stats['pcv'] / user_fei

    total_supply = await total_supply_task
    protocol_fei = [
        block_total_supply - block_user_fei
        for block_total_supply, block_user_fei in zip(total_supply, user_fei)
    ]

    return {
        'pcv_stats': {
            'PCV Total': {'values': list(pcv_total.values)},
            'Collateralization Ratio': {'values': list(cr.values)},
        },
        'circulating_fei': {
            'User FEI': {'values': list(user_fei.values)},
            'Protocol FEI': {'values': protocol_fei},
        },
    }


async def async_compute_pcv_by_asset(blocks, verbose=False):
    return {
        'ETH': {'values': [9999] * len(blocks)},
        'RAI': {'values': [9999] * len(blocks)},
        'LUSD': {'values': [9999] * len(blocks)},
        'DAI': {'values': [9999] * len(blocks)},
        'DPI': {'values': [9999] * len(blocks)},
        'INDEX': {'values': [9999] * len(blocks)},
        'BAL': {'values': [9999] * len(blocks)},
    }


async def async_compute_pcv_by_deployment(blocks, verbose=False):
    return {
        'Tokemak': {'values': [9999] * len(blocks)},
        'Lido': {'values': [9999] * len(blocks)},
        'Uniswap': {'values': [9999] * len(blocks)},
        'Rari': {'values': [9999] * len(blocks)},
        'Sushi': {'values': [9999] * len(blocks)},
        'Fei': {'values': [9999] * len(blocks)},
        'Aave': {'values': [9999] * len(blocks)},
        'Compound': {'values': [9999] * len(blocks)},
    }

