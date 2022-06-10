from __future__ import annotations

from ctc import evm
from ctc import rpc
from ctc import spec


async def async_get_eth_total_supply(
    network: spec.NetworkReference | None,
) -> int | float:
    import aiohttp

    if network is None:
        network = rpc.get_provider(None)['network']
    if network != 'mainnet':
        raise NotImplementedError('total supply only implemented for mainnet')
    if isinstance(network, int):
        network = evm.get_network_name(network)

    url = 'http://api.etherscan.io/api?module=stats&action=ethsupply'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception('could not get result')
            result = await response.json()
            return int(result['result'])
