import asyncio

from . import spec
from . import metric_groups


async def async_get_metrics(
    blocks: list[int],
    verbose: bool = False,
) -> dict[spec.MetricGroupName, spec.MetricGroup]:

    names = [
        'pcv_stats',
        'pcv_by_asset',
        'pcv_by_deployment',
        'prices',
        'dex_volume',
        'dex_tvl',
        # 'circulating_fei',
        'pfei_by_deployment',
        'buybacks',
    ]
    kwargs = {'blocks': blocks, 'verbose': verbose}
    metrics = await asyncio.gather(
        metric_groups.async_compute_pcv_stats(**kwargs),
        metric_groups.async_compute_pcv_by_asset(**kwargs),
        metric_groups.async_compute_pcv_by_deployment(**kwargs),
        metric_groups.async_compute_prices(**kwargs),
        metric_groups.async_compute_dex_volume(**kwargs),
        metric_groups.async_compute_dex_tvls(**kwargs),
        metric_groups.async_compute_pfei_by_deployment(**kwargs),
        metric_groups.async_compute_buybacks(**kwargs),
    )
    payload = dict(zip(names, metrics))
    pcv_stats = payload.pop('pcv_stats')
    payload['pcv_stats'] = pcv_stats['pcv_stats']
    payload['circulating_fei'] = pcv_stats['circulating_fei']
    return payload

