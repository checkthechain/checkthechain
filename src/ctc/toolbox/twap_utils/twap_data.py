from __future__ import annotations

from ctc import spec
from . import twap_data_sources
from . import twap_spec


async def async_get_data_feed(
    data_source: twap_spec.DataSource,
    start_block: int,
    end_block: int,
    provider: spec.ProviderSpec = None,
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
        return await twap_data_sources.async_get_uniswap_v2_data(
            start_block=start_block,
            end_block=end_block,
            data_source=data_source,
            provider=provider,
        )
    else:
        raise Exception('unknown data source protocol: ' + str(protocol))

