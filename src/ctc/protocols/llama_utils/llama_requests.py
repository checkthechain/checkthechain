from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    class TVLTimeseries(TypedDict):
        timestamp: typing.Sequence[int]
        tvl: typing.Sequence[int | float]

    class YieldTimeseries(TypedDict):
        timestamp: typing.Sequence[int]
        tvl: typing.Sequence[int | float]
        apy: typing.Sequence[int | float]


from typing_extensions import Literal

import aiohttp


tvl_url_root = 'https://api.llama.fi'
yields_url_root = 'https://yields.llama.fi'

url_templates = {
    'historical_defi_tvl': '/charts',
    'protocols_tvls': '/protocols',
    'historical_protocol_tvl': '/protocol/{protocol}',
    'chains_tvls': '/chains',
    'historical_chain_tvl': '/charts/{chain}',
    'pools': '/pools',
    'pool_yield': '/chart/{pool}',
}


async def async_request_llama_data(
    datatype: str, **parameters: typing.Any
) -> typing.Any:

    if datatype in ['pools', 'pool_yield']:
        root = yields_url_root
    else:
        root = tvl_url_root

    # create url
    if parameters is None:
        parameters = {}
    url = root + url_templates[datatype].format(**parameters)

    # make request
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def async_get_historical_defi_tvl() -> TVLTimeseries:
    data = await async_request_llama_data('historical_defi_tvl')

    dates = []
    tvls = []
    for datum in data:
        dates.append(int(datum['date']))
        tvls.append(datum['totalLiquidityUSD'])

    return {'timestamp': dates, 'tvl': tvls}


async def async_get_protocols_tvls(
    *,
    n: int | None = None,
    category: str | None = None,
    chain: str | None = None,
) -> typing.Sequence[typing.Any]:
    data = await async_request_llama_data('protocols_tvls')

    filtered = []
    for datum in data:

        if category is not None and datum['category'] != category:
            continue

        if chain is not None and chain not in datum['chains']:
            continue

        filtered.append(datum)

        if n is not None and len(filtered) >= n:
            break

    return filtered


async def async_get_historical_protocol_tvl(protocol: str) -> typing.Any:

    data = await async_request_llama_data(
        'historical_protocol_tvl', protocol=protocol
    )

    return data


async def async_get_chains_tvls() -> typing.Sequence[typing.Any]:
    data: typing.Sequence[typing.Any] = await async_request_llama_data('chains_tvls')

    return data


async def async_get_historical_chain_tvl(chain: str) -> TVLTimeseries:

    data = await async_request_llama_data('historical_chain_tvl', chain=chain)

    timestamp = []
    tvl = []

    for datum in data:
        timestamp.append(int(datum['date']))
        tvl.append(datum['totalLiquidityUSD'])

    return {'timestamp': timestamp, 'tvl': tvl}


async def async_get_llama_pools(
    *,
    chain: str | None = None,
    project: str | None = None,
    stablecoin: bool | None = None,
    exposure: Literal['single', 'multi'] | None = None,
    min_apy: typing.SupportsFloat | None = None,
    max_apy: typing.SupportsFloat | None = None,
    min_tvl: typing.SupportsFloat | None = None,
    max_tvl: typing.SupportsFloat | None = None,
) -> typing.Sequence[typing.Any]:

    data = await async_request_llama_data('pools')

    if min_apy is not None:
        min_apy = float(min_apy)
    if max_apy is not None:
        max_apy = float(max_apy)
    if min_tvl is not None:
        min_tvl = float(min_tvl)
    if max_tvl is not None:
        max_tvl = float(max_tvl)

    pools = []
    for pool in data['data']:
        if chain is not None and pool['chain'] != chain:
            continue
        if project is not None and pool['project'] != project:
            continue
        if stablecoin is not None and pool['stablecoin'] != stablecoin:
            continue
        if exposure is not None and pool['exposure'] != exposure:
            continue
        if min_apy is not None and pool['apy'] < min_apy:
            continue
        if max_apy is not None and pool['apy'] > max_apy:
            continue
        if min_tvl is not None and pool['tvlUsd'] < min_tvl:
            continue
        if max_tvl is not None and pool['tvlUsd'] > max_tvl:
            continue

        pools.append(pool)

    return pools


async def async_get_pool_yield(pool: str) -> YieldTimeseries:

    import tooltime

    response = await async_request_llama_data('pool_yield', pool=pool)

    timestamp = []
    tvl = []
    apy = []
    for datum in response['data']:
        timestamp.append(tooltime.timestamp_to_seconds(datum['timestamp']))
        tvl.append(datum['tvlUsd'])
        apy.append(datum['apy'])

    return {
        'timestamp': timestamp,
        'tvl': tvl,
        'apy': apy,
    }
