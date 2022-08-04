from __future__ import annotations

import typing


vaults_endpoint = 'https://api.yearn.finance/v1/chains/1/vaults/all'


async def async_request_yearn_api_v1_data() -> typing.Sequence[typing.Any]:
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(vaults_endpoint) as response:
            pools: typing.Sequence[typing.Any] = await response.json()
            return pools
