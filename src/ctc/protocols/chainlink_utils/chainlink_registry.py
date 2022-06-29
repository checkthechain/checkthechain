from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec


feed_registry = {
    # mainnet
    1: '0x47fb2585d2c56fe188d0e6ec628a38b74fceeedf',
    # kovan
    42: '0xAa7F6f7f507457a1EE157fE97F6c7DB2BEec5cD0',
}

feed_registry_asset_addresses = {
    'BTC': '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    'ETH': '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
    'USD': '0x0000000000000000000000000000000000000348',
    'GBP': '0x000000000000000000000000000000000000033a',
    'EUR': '0x00000000000000000000000000000000000003d2',
}

feed_registry_address_assets = {
    v: k for k, v in feed_registry_asset_addresses.items()
}

registry_function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'getFeed': {
        'inputs': [
            {'internalType': 'address', 'name': 'base', 'type': 'address'},
            {'internalType': 'address', 'name': 'quote', 'type': 'address'},
        ],
        'name': 'getFeed',
        'outputs': [
            {
                'internalType': 'contract AggregatorV2V3Interface',
                'name': 'aggregator',
                'type': 'address',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPhaseRange': {
        'inputs': [
            {'internalType': 'address', 'name': 'base', 'type': 'address'},
            {'internalType': 'address', 'name': 'quote', 'type': 'address'},
            {'internalType': 'uint16', 'name': 'phaseId', 'type': 'uint16'},
        ],
        'name': 'getPhaseRange',
        'outputs': [
            {
                'internalType': 'uint80',
                'name': 'startingRoundId',
                'type': 'uint80',
            },
            {
                'internalType': 'uint80',
                'name': 'endingRoundId',
                'type': 'uint80',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPhase': {
        'inputs': [
            {'internalType': 'address', 'name': 'base', 'type': 'address'},
            {'internalType': 'address', 'name': 'quote', 'type': 'address'},
            {'internalType': 'uint16', 'name': 'phaseId', 'type': 'uint16'},
        ],
        'name': 'getPhase',
        'outputs': [
            {
                'components': [
                    {
                        'internalType': 'uint16',
                        'name': 'phaseId',
                        'type': 'uint16',
                    },
                    {
                        'internalType': 'uint80',
                        'name': 'startingAggregatorRoundId',
                        'type': 'uint80',
                    },
                    {
                        'internalType': 'uint80',
                        'name': 'endingAggregatorRoundId',
                        'type': 'uint80',
                    },
                ],
                'internalType': 'struct FeedRegistryInterface.Phase',
                'name': 'phase',
                'type': 'tuple',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
}


async def async_get_registry_feed(
    base: str,
    quote: str,
    *,
    provider: spec.ProviderReference = None,
) -> spec.Address:
    network = rpc.get_provider_network(provider)
    registry_address = feed_registry[network]

    result = await rpc.async_eth_call(
        to_address=registry_address,
        function_abi=registry_function_abis['getFeed'],
        function_parameters=[base, quote],
        provider=provider,
    )

    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_phase_range(
    *,
    base: str,
    quote: str,
    phase: int,
    provider: spec.ProviderReference = None,
) -> typing.Tuple[int, ...]:
    network = rpc.get_provider_network(provider)
    registry_address = feed_registry[network]

    result = await rpc.async_eth_call(
        to_address=registry_address,
        # function_abi=registry_function_abis['getPhaseRange'],
        function_abi=registry_function_abis['getPhase'],
        function_parameters=[base, quote, phase],
        provider=provider,
    )

    if not isinstance(result, tuple) or not all(
        isinstance(item, int) for item in result
    ):
        raise Exception('invalid rpc result')
    return result
