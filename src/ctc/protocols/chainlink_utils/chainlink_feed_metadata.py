from __future__ import annotations

import typing

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
    context: spec.Context = None,
) -> chainlink_db.ChainlinkFeed:
    query = _build_feed_query(feed)
    feed_data = await chainlink_db.async_query_feed(context=context, **query)
    if feed_data is None:
        raise Exception('could not find data for feed: ' + str(feed))
    return feed_data


async def async_get_feed_decimals(
    feed: chainlink_spec._FeedReference,
    *,
    context: spec.Context = None,
) -> int:

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='chainlink', context=context
    )

    # try database
    if read_cache:
        query = _build_feed_query(feed)
        feed_data = await chainlink_db.async_query_feed(
            context=context, **query
        )
        if feed_data is not None:
            return feed_data['decimals']

    # query rpc
    if evm.is_address_str(feed):
        result = await rpc.async_eth_call(
            feed,
            function_abi=chainlink_spec.feed_function_abis['decimals'],
            context=context,
        )
        if not isinstance(result, int):
            raise Exception('invalid rpc result')
        return result

    else:
        raise Exception('could not find address for feed: ' + str(feed))


async def async_resolve_feed_address(
    feed: str,
    *,
    context: spec.Context = None,
) -> spec.Address:

    if evm.is_address_str(feed):
        return feed

    query = _build_feed_query(feed)
    feed_data = await chainlink_db.async_query_feed(context=context, **query)
    if feed_data is not None:
        return feed_data['address']
    else:
        raise Exception('could not resolve feed address')


async def async_get_feed_aggregator(
    feed: chainlink_spec._FeedReference,
    *,
    block: spec.BlockNumberReference = 'latest',
    fill_empty: bool = True,
    context: spec.Context = None,
) -> spec.Address:

    feed = await async_resolve_feed_address(feed, context=context)

    aggregator = await rpc.async_eth_call(
        to_address=feed,
        function_abi=chainlink_spec.feed_function_abis['aggregator'],
        block_number=block,
        fill_empty=fill_empty,
        context=context,
    )
    if aggregator is None:
        raise Exception('aggregator not specified')
    if not isinstance(aggregator, str):
        raise Exception('invalid rpc result')

    return aggregator


async def async_get_feed_first_block(
    feed: chainlink_spec._FeedReference,
    *,
    start_search: typing.Optional[spec.BlockNumberReference] = None,
    end_search: typing.Optional[spec.BlockNumberReference] = None,
    verbose: bool = False,
    context: spec.Context = None,
) -> int:

    feed = await async_resolve_feed_address(feed, context=context)

    creation_block = await evm.async_get_contract_creation_block(
        contract_address=feed,
        start_block=start_search,
        end_block=end_search,
        verbose=verbose,
        context=context,
    )

    if creation_block is None:
        raise Exception('could not determine creation_block for feed')

    return creation_block

