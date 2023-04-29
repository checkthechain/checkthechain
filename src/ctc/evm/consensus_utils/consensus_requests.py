from __future__ import annotations

import typing

from ctc import spec
from . import consensus_spec


def _get_consensus_node_host(context: spec.Context) -> str:
    from ctc import config

    chain_id = config.get_context_chain_id(context)
    if chain_id == 1:
        return 'http://testing.mainnet.beacon-api.nimbus.team'
    elif chain_id == 5:
        return 'http://unstable.prater.beacon-api.nimbus.team'
    else:
        raise Exception(
            'no known consensus node for chain_id = ' + str(chain_id)
        )


def _build_consensus_url(
    endpoint: str,
    *,
    context: spec.Context,
    params: typing.Mapping[str, typing.Any] | None = None,
) -> str:
    host = _get_consensus_node_host(context=context)
    if params is None:
        params = {}
    return host + consensus_spec.consensus_endpoints[endpoint].format(**params)


async def async_beacon_request(
    endpoint: str,
    *,
    params: typing.Mapping[str, typing.Any] | None = None,
    context: spec.Context = None,
) -> typing.Any:
    import aiohttp

    url = _build_consensus_url(
        endpoint=endpoint, context=context, params=params
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data['data']


def _sync_beacon_request(
    endpoint: str,
    *,
    params: typing.Mapping[str, typing.Any] | None = None,
    context: spec.Context = None,
) -> typing.Any:
    import requests

    url = _build_consensus_url(
        endpoint=endpoint, context=context, params=params
    )
    response = requests.get(url)
    return response.json()['data']

