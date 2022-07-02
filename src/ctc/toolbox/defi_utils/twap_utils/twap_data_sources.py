from __future__ import annotations

import typing

from ctc import spec
from . import twap_spec


async def async_get_chainlink_data(
    data_source: twap_spec.DataSource,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> spec.Series:

    from ctc.protocols import chainlink_utils

    feed = data_source.get('feed')
    composite_feed = data_source.get('composite_feed')
    invert = data_source.get('invert')
    if invert is None:
        invert = False
    normalize = data_source.get('normalize')
    if normalize is None:
        normalize = False

    if feed is not None:
        return await chainlink_utils.async_get_feed_data(
            feed=feed,
            invert=invert,
            normalize=normalize,
            start_block=start_block,
            end_block=end_block,
            interpolate=True,
            fields='answer',
            provider=provider,
        )
    elif composite_feed is not None:
        return await chainlink_utils.async_get_composite_feed_data(
            composite_feed=composite_feed,
            invert=invert,
            start_block=start_block,
            end_block=end_block,
            provider=provider,
        )
    else:
        raise Exception('must specify feed or composite_feed')


# async def async_get_uniswap_v2_data(
#     data_source: twap_spec.DataSource,
#     start_block: typing.Optional[spec.BlockNumberReference] = None,
#     end_block: typing.Optional[spec.BlockNumberReference] = None,
#     provider: spec.ProviderReference = None,
# ) -> spec.Series:

#     from ctc.protocols import uniswap_v2_utils

#     feed = data_source.get('feed')
#     composite_feed = data_source.get('composite_feed')
#     invert = data_source.get('invert')
#     normalize = data_source.get('normalize')

#     if feed is not None:
#         return await uniswap_v2_utils.async_get_feed_data(
#             feed=feed,
#             invert=invert,
#             normalize=normalize,
#             start_block=start_block,
#             end_block=end_block,
#             interpolate=True,
#             provider=provider,
#         )
#     elif composite_feed is not None:
#         return await uniswap_v2_utils.async_get_composite_feed_data(
#             composite_feed=composite_feed,
#             invert=invert,
#             normalize=normalize,
#             start_block=start_block,
#             end_block=end_block,
#             provider=provider,
#         )
#     else:
#         raise Exception('must specify feed or composite_feed')
