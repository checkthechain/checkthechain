import asyncio

from ctc import evm
from ctc import spec
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
            'metrics': {
                'pcv_total': {
                    'name': 'PCV Total',
                    'values': list(pcv_total.values),
                },
                'cr': {
                    'name': 'Collateralization Ratio',
                    'values': list(cr.values),
                },
            },
        },
        'circulating_fei': {
            'name': 'Circulating FEI',
            'metrics': {
                'user_fei': {
                    'name': 'User FEI',
                    'values': list(user_fei.values),
                },
                'protocol_fei': {
                    'name': 'Protocol FEI',
                    'values': protocol_fei,
                },
            },
        },
    }


async def async_compute_pcv_by_asset(
    blocks: list[int], verbose: bool = False, provider: spec.ProviderSpec = None
):

    tokens_balances = await fei_utils.async_get_tokens_balances_by_block(
        blocks=blocks,
        usd=True,
        exclude_fei=True,
    )

    tokens = list(tokens_balances.keys())

    symbols = await fei_utils.async_get_pcv_tokens_symbols(
        tokens=tokens,
        provider=provider,
        block=blocks[-1],
    )

    metrics = {}
    for token in tokens:
        symbol = symbols[token]
        metrics[symbol] = {
            'name': symbol,
            'values': tokens_balances[token],
            'units': 'USD',
        }

    return {'name': 'PCV by Asset', 'metrics': metrics}


async def async_compute_pcv_by_deployment(
    blocks: list[int], verbose: bool = False
) -> analytics_spec.MetricGroup:
    metrics: dict[str, analytics_spec.MetricData] = {
        'tokemak': {'name': 'Tokemak', 'values': [9999] * len(blocks)},
        'lido': {'name': 'Lido', 'values': [9999] * len(blocks)},
        'uniswap': {'name': 'Uniswap', 'values': [9999] * len(blocks)},
        'rari': {'name': 'Rari', 'values': [9999] * len(blocks)},
        'sushi': {'name': 'Sushi', 'values': [9999] * len(blocks)},
        'fei': {'name': 'Fei', 'values': [9999] * len(blocks)},
        'aave': {'name': 'Aave', 'values': [9999] * len(blocks)},
        'compound': {'name': 'Compound', 'values': [9999] * len(blocks)},
    }

    return {
        'name': 'PCV by Deployment',
        'metrics': metrics,
    }

