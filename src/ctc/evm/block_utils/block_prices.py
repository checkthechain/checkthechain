from __future__ import annotations


async def async_compute_block_eth_prices(
    blocks: typing.Sequence[int] | spec.Series,
    context: spec.Context = None,
) -> spec.Series:
    import polars as pl
    from ctc.protocols import chainlink_utils

    start_block = min(blocks)
    end_block = max(blocks)
    ETH_USD = await chainlink_utils.async_get_feed_data(
        'ETH_USD',
        context=context,
        interpolate=True,
        start_block=start_block,
        end_block=end_block,
    )
    df = pl.DataFrame(blocks.alias('block_number'))
    joined = df.join(ETH_USD, on='block_number', how='left')
    return joined['answer'].alias('ETH_USD')

