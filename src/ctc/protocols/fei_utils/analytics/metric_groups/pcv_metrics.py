import asyncio

from ctc import evm
from ctc.protocols import fei_utils
from .. import analytics_spec


async def async_compute_pcv_stats(
    blocks: list[int],
    verbose: bool = False,
) -> dict[str, analytics_spec.MetricGroup]:

    pcv_stats_task = asyncio.create_task(
        fei_utils.async_get_pcv_stats(blocks=blocks)
    )
    total_supply_task = asyncio.create_task(
        evm.async_get_erc20_total_supply_by_block(token='FEI', blocks=blocks)
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
            'name': 'PCV Statistics',
            'metrics': [
                {'name': 'PCV Total', 'values': list(pcv_total.values)},
                {'name': 'Collateralization Ratio', 'values': list(cr.values)},
            ],
        },
        'circulating_fei': {
            'name': 'Circulating FEI',
            'metrics': [
                {'name': 'User FEI', 'values': list(user_fei.values)},
                {'name': 'Protocol FEI', 'values': protocol_fei},
            ],
        },
    }


async def async_compute_pcv_by_asset(
    blocks: list[int], verbose: bool = False
) -> analytics_spec.MetricGroup:
    metrics: list[analytics_spec.MetricData] = [
        {'name': 'ETH', 'values': [9999] * len(blocks)},
        {'name': 'RAI', 'values': [9999] * len(blocks)},
        {'name': 'LUSD', 'values': [9999] * len(blocks)},
        {'name': 'DAI', 'values': [9999] * len(blocks)},
        {'name': 'DPI', 'values': [9999] * len(blocks)},
        {'name': 'INDEX', 'values': [9999] * len(blocks)},
        {'name': 'BAL', 'values': [9999] * len(blocks)},
    ]
    return {
        'name': 'PCV By Asset',
        'metrics': metrics,
    }


async def async_compute_pcv_by_deployment(
    blocks: list[int], verbose: bool = False
) -> analytics_spec.MetricGroup:
    metrics: list[analytics_spec.MetricData] = [
        {'name': 'Tokemak', 'values': [9999] * len(blocks)},
        {'name': 'Lido', 'values': [9999] * len(blocks)},
        {'name': 'Uniswap', 'values': [9999] * len(blocks)},
        {'name': 'Rari', 'values': [9999] * len(blocks)},
        {'name': 'Sushi', 'values': [9999] * len(blocks)},
        {'name': 'Fei', 'values': [9999] * len(blocks)},
        {'name': 'Aave', 'values': [9999] * len(blocks)},
        {'name': 'Compound', 'values': [9999] * len(blocks)},
    ]

    return {
        'name': 'PCV by Deployment',
        'metrics': metrics,
    }

