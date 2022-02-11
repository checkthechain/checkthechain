from __future__ import annotations

import asyncio

from . import analytics_spec
from . import metric_groups


f_metric_group: dict[str, analytics_spec.MetricGroupCreatorCoroutine] = {
    'pcv_by_asset': metric_groups.async_compute_pcv_by_asset,
    'prices': metric_groups.async_compute_prices,
    'dex_volume': metric_groups.async_compute_dex_volume,
    'dex_tvls': metric_groups.async_compute_dex_tvls,
    'pfei_by_platform': metric_groups.async_compute_pfei_by_platform,
    'buybacks': metric_groups.async_compute_buybacks,
}
f_multi_metric_group: dict[
    str, analytics_spec.MultiMetricGroupCreatorCoroutine
] = {
    'pcv_stats': metric_groups.async_compute_pcv_stats,
}


async def async_get_metrics(
    blocks: list[int],
    verbose: bool = False,
) -> dict[str, analytics_spec.MetricGroup]:

    # create coroutines
    mg_coroutines = [f(blocks, verbose) for f in f_metric_group.values()]
    mg_task = asyncio.gather(*mg_coroutines)
    mmg_coroutines = [f(blocks, verbose) for f in f_multi_metric_group.values()]
    mmg_task = asyncio.gather(*mmg_coroutines)

    # build payload
    payload = {}
    mg_results = await mg_task
    for key, mg_result in zip(f_metric_group.keys(), mg_results):
        payload[key] = mg_result
    mmg_results = await mmg_task
    for mmg_result in mmg_results:
        for key, value in mmg_result.items():
            payload[key] = value

    # add missing orders
    for key, metric_group in payload.items():
        if 'order' not in metric_group:
            metric_group['order'] = order_metrics_in_group(
                metric_group['metrics']
            )

    return payload


def order_metrics_in_group(
    metrics: dict[str, analytics_spec.MetricData]
) -> list[str]:
    """order metrics in descending order by their final values"""
    pairs = [
        (metric_data['values'][-1], metric_name)
        for metric_name, metric_data in metrics.items()
    ]
    pairs = sorted(pairs, reverse=True)
    return [pair[-1] for pair in pairs]

