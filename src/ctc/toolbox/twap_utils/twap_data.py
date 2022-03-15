from __future__ import annotations


async def async_get_data_feed(
) -> spec.Series:
    # acquire data
    protocol = data_source['protocol']
    if protocol == 'chainlink':
        return await twap_data_sources.async_get_chainlink_data(
            start_block=start_block,
            end_block=end_block,
            data_source=data_source,
            provider=provider,
        )
    elif protocol == 'uniswap_v2':
        return await twap_data_sources.async_get_chainlink_data(
            start_block=start_block,
            end_block=end_block,
            data_source=data_source,
            provider=provider,
        )
    else:
        raise Exception('unknown data source protocol: ' + str(protocol))


async def async_get_chainlink_data(
    data_source: DataSource,
    start_block: int,
    end_block: int,
) -> spec.Series:

    from ctc.protocols import chainlink_utils

    feed = data_source.get('feed')
    composite_feed = data_source.get('composite_feed')
    invert = data_source.get('invert')
    normalize = data_source.get('normalize')

    if feed is not None:
        return await chainlink_utils.async_get_feed_data(
            feed=feed,
            invert=invert,
            normalize=normalize,
            start_block=start_block,
            end_block=end_block,
            interpolate=True,
        )
    elif composite_feed is not None:
        return await chainlink_utils.async_get_composite_feed_data(
            composite_feed=composite_feed,
            invert=invert,
            normalize=normalize,
            start_block=start_block,
            end_block=end_block,
        )
    else:
        raise Exception('must specify feed or composite_feed')


async def async_get_uniswap_v2_data(
    data_source: DataSource,
    start_block: int,
    end_block: int,
):

    from ctc.protocols import uniswap_v2_utils

    feed = data_source.get('feed')
    composite_feed = data_source.get('composite_feed')
    invert = data_source.get('invert')
    normalize = data_source.get('normalize')

    if feed is not None:
        return await uniswap_v2_utils.async_get_feed_data(
            feed=feed,
            invert=invert,
            normalize=normalize,
            start_block=start_block,
            end_block=end_block,
            interpolate=True,
        )
    elif composite_feed is not None:
        return await uniswap_v2_utils.async_get_composite_feed_data(
            composite_feed=composite_feed,
            invert=invert,
            normalize=normalize,
            start_block=start_block,
            end_block=end_block,
        )
    else:
        raise Exception('must specify feed or composite_feed')

