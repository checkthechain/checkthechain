from __future__ import annotations

from ctc import config
from ctc import spec


async def async_get_eth_total_supply(
    *,
    context: spec.Context = None,
) -> int | float:
    import aiohttp

    chain_id = config.get_context_chain_id(context)
    if chain_id != 1:
        raise NotImplementedError('total supply only implemented for ethereum')

    url = 'http://api.etherscan.io/api?module=stats&action=ethsupply'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception('could not get result')
            result = await response.json()
            return int(result['result'])
