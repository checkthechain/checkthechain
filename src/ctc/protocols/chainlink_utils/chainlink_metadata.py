from __future__ import annotations

import asyncio
import typing

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc import spec

from . import chainlink_spec


async def async_get_feed_decimals(
    feed: chainlink_spec._FeedReference,
    provider: spec.ProviderSpec = None,
) -> int:
    provider = rpc.get_provider(provider)
    feed = await async_resolve_feed_address(feed, provider=provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')
    metadata = directory.get_oracle_feed_metadata(
        address=feed,
        network=network,
        protocol='chainlink',
    )
    return metadata['decimals']


async def async_get_aggregator_description(
    aggregator: spec.Address,
    provider: spec.ProviderSpec = None,
) -> str:

    function_abi = {
        'inputs': [],
        'name': 'description',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    }

    provider = rpc.get_provider(provider)
    return rpc.async_eth_call(
        to_address=aggregator,
        provider=provider,
        function_abi=function_abi,
    )


async def async_get_aggregator_base_quote(
    aggregator: spec.Address, provider: spec.ProviderSpec = None,
) -> dict[str, str]:
    description = await async_get_aggregator_description(
        aggregator=aggregator,
        provider=provider,
    )
    try:
        base, quote = description.split(' / ')
        return {'base': base, 'quote': quote}
    except Exception:
        raise Exception(
            'could not determine base or quote from description: '
            + str(description)
        )


async def async_resolve_feed_address(
    feed: str,
    *,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference = 'latest',
) -> spec.Address:

    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    if evm.is_address_str(feed):
        return feed
    elif isinstance(feed, str):
        return directory.get_oracle_address(
            name=feed,
            protocol='chainlink',
            network=network,
            block=block,
        )
    else:
        raise Exception('invalid feed reference: ' + str(feed))


async def async_get_feed_aggregator(
    feed: chainlink_spec._FeedReference,
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
    fill_empty: bool = True,
) -> spec.Address:

    feed = await async_resolve_feed_address(
        feed, block=block, provider=provider
    )

    aggregator = await rpc.async_eth_call(
        to_address=feed,
        function_abi=chainlink_spec.feed_function_abis['aggregator'],
        block_number=block,
        fill_empty=fill_empty,
    )

    if aggregator is None:
        raise Exception('aggregator not specified')

    return aggregator


async def async_get_feed_aggregator_history(
    feed: str, provider: spec.ProviderSpec
) -> list[spec.Address]:

    previous_aggregators = await async_get_feed_previous_aggregators(
        feed=feed, provider=provider
    )


async def async_get_feed_previous_aggregators(
    feed: str, provider: spec.ProviderSpec
) -> list[spec.Address]:

    feed = await async_resolve_feed_address(feed, provider=provider)

    current_phase = await rpc.async_eth_call(
        to_address=feed,
        function_name='phaseId',
    )

    coroutines = [
        rpc.async_eth_call(
            to_address=feed,
            function_name='phaseAggregators',
            function_parameters=[i],
        )
        for i in range(1, current_phase + 1)
    ]
    aggregators = await asyncio.gather(*coroutines)

    return aggregators


async def async_get_feed_first_block(
    feed: chainlink_spec._FeedReference,
    provider: spec.ProviderSpec = None,
    start_search: typing.Optional[spec.BlockNumberReference] = None,
    end_search: typing.Optional[spec.BlockNumberReference] = None,
    verbose: bool = False,
) -> int:

    feed = await async_resolve_feed_address(feed, provider=provider)

    creation_block = await evm.async_get_contract_creation_block(
        contract_address=feed,
        start_block=start_search,
        end_block=end_search,
        verbose=verbose,
    )

    if creation_block is None:
        raise Exception('could not determine creation_block for feed')

    return creation_block

