"""
see also
    https://meta.yearn.finance/api/1/vaults/all
    https://meta.yearn.finance/api/1/protocols/all
    https://meta.yearn.finance/api/1/tokens/all
    https://meta.yearn.finance/api/1/strategies/all
"""

from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from . import yearn_spec


vaults_endpoint = 'https://api.yearn.finance/v1/chains/{chain_id}/vaults/all'


async def async_get_yearn_api_vaults(
    network: spec.NetworkReference,
) -> typing.Sequence[yearn_spec.ApiVault]:
    import aiohttp

    chain_id = evm.get_network_chain_id(network)
    url = vaults_endpoint.format(chain_id=chain_id)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            vaults: typing.Sequence[yearn_spec.ApiVault] = await response.json()
            return vaults


async def async_get_yearn_api_vault(
    query: str,
    network: spec.NetworkReference,
    *,
    api_vaults: typing.Sequence[typing.Any] | None = None,
) -> yearn_spec.ApiVault:
    """

    Query will return the first of the following that matches:
    - query is an address of a vault
    - query equals the name of a vault
    - query equals the symbol of a vault (result whichever has latest version)

    All queries are considered case insensitive
    """

    # obtain api data
    if api_vaults is None:
        api_vaults = await async_get_yearn_api_vaults(network=network)

    # check if query matches an address
    query = query.lower()
    if evm.is_address_str(query):
        for vault in api_vaults:
            if vault['address'].lower() == query:
                return vault

    # check if query matches a name
    for vault in api_vaults:
        if query == vault['name'].lower():
            return vault

    # check if query matches a symbol
    candidates = []
    for vault in api_vaults:
        if query == vault['symbol'].lower():
            candidates.append(vault)
    if len(candidates) == 0:
        raise Exception('vault could not be found')
    elif len(candidates) == 1:
        return candidates[0]
    else:
        # TODO: more robust determination of latest vault
        ordered = sorted(
            candidates, key=lambda candidate: candidate['name']
        )
        latest = ordered[-1]
        return latest
