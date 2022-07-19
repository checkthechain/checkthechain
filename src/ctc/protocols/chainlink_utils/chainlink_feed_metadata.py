from __future__ import annotations

import typing

from ctc import config
from ctc import evm
from ctc import rpc
from ctc import spec

from . import chainlink_db
from . import chainlink_spec


def _build_feed_query(
    feed: chainlink_spec._FeedReference,
) -> typing.Mapping[str, typing.Any]:
    if isinstance(feed, str):
        if evm.is_address_str(feed):
            return {'address': feed}
        elif '_' in feed:
            return {'name': feed.replace('_', ' / ')}
        else:
            return {'name': feed}
    else:
        raise Exception('unknown feed reference type')


async def async_get_feed_metadata(
    feed: chainlink_spec._FeedReference,
    *,
    network: spec.NetworkReference | None = None,
) -> chainlink_db.ChainlinkFeed:
    query = _build_feed_query(feed)
    if network is None:
        network = config.get_default_network()

    feed_data = await chainlink_db.async_query_feed(network=network, **query)
    if feed_data is None:
        raise Exception('could not find data for feed: ' + str(feed))
    return feed_data


async def async_get_feed_decimals(
    feed: chainlink_spec._FeedReference,
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
    use_db: bool = True,
) -> int:

    # try database
    if use_db:
        query = _build_feed_query(feed)
        if network is None:
            if provider is not None:
                network = rpc.get_provider_network(provider)
            else:
                network = config.get_default_network()

        feed_data = await chainlink_db.async_query_feed(
            network=network, **query
        )
        if feed_data is not None:
            return feed_data['decimals']

    # query rpc
    if evm.is_address_str(feed):
        if provider is None and network is not None:
            provider = {'network': network}
        result = await rpc.async_eth_call(
            feed,
            provider=provider,
            function_abi=chainlink_spec.feed_function_abis['decimals'],
        )
        if not isinstance(result, int):
            raise Exception('invalid rpc result')
        return result

    else:
        raise Exception('could not find address for feed: ' + str(feed))


async def async_resolve_feed_address(
    feed: str,
    *,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> spec.Address:

    if evm.is_address_str(feed):
        return feed

    query = _build_feed_query(feed)
    if network is None:
        if provider is not None:
            network = rpc.get_provider_network(provider)
        else:
            network = config.get_default_network()

    feed_data = await chainlink_db.async_query_feed(network=network, **query)
    if feed_data is not None:
        return feed_data['address']
    else:
        raise Exception('could not resolve feed address')


async def async_get_feed_aggregator(
    feed: chainlink_spec._FeedReference,
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderReference = None,
    fill_empty: bool = True,
) -> spec.Address:

    feed = await async_resolve_feed_address(feed, provider=provider)

    aggregator = await rpc.async_eth_call(
        to_address=feed,
        function_abi=chainlink_spec.feed_function_abis['aggregator'],
        block_number=block,
        fill_empty=fill_empty,
    )
    if aggregator is None:
        raise Exception('aggregator not specified')
    if not isinstance(aggregator, str):
        raise Exception('invalid rpc result')

    return aggregator


async def async_get_feed_first_block(
    feed: chainlink_spec._FeedReference,
    *,
    provider: spec.ProviderReference = None,
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
