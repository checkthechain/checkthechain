import typing

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc import spec

from . import chainlink_spec


def get_feed_decimals(
    feed: chainlink_spec._FeedReference,
    provider: spec.ProviderSpec = None,
):
    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')
    metadata = directory.get_oracle_feed_metadata(
        address=feed,
        network=network,
        protocol='chainlink',
    )
    return metadata['decimals']


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
) -> spec.Address:

    feed = await async_resolve_feed_address(
        feed, block=block, provider=provider
    )

    return await rpc.async_eth_call(
        to_address=feed,
        function_name='aggregator',
        block_number=block,
    )


async def async_get_feed_first_block(
    feed: chainlink_spec._FeedReference,
    provider: spec.ProviderSpec = None,
    start_search: typing.Optional[spec.BlockNumberReference] = None,
    end_search: typing.Optional[spec.BlockNumberReference] = None,
    verbose: bool = False,
) -> int:

    feed = await async_resolve_feed_address(feed, provider=provider)

    return await evm.async_get_contract_creation_block(
        contract_address=feed,
        start_block=start_search,
        end_block=end_search,
        verbose=verbose,
    )

