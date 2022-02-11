from __future__ import annotations

import os
import typing

import toolcache

import ctc.config
from ctc.toolbox import search_utils
from ctc.toolbox import store_utils
from ctc import spec


def get_oracle_address(
    name: str,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
    oracle_type: spec.Oracletype = 'feed',
    block: spec.BlockNumberReference = 'latest',
):

    oracle = get_oracle_metadata(
        name=name,
        network=network,
        protocol=protocol,
        oracle_type=oracle_type,
        block=block,
    )
    return oracle['address']


def get_oracle_name(
    address: spec.Address,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
    oracle_type: spec.Oracletype = 'feed',
    block: spec.BlockNumberReference = 'latest',
):
    oracle = get_oracle_metadata(
        address=address,
        network=network,
        protocol=protocol,
        oracle_type=oracle_type,
        block=block,
    )
    return oracle['name']


def has_oracle_metadata(
    name: typing.Optional[str] = None,
    *,
    address: typing.Optional[spec.Address] = None,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
) -> bool:
    try:
        get_oracle_metadata(
            name=name, address=address, network=network, protocol=protocol
        )
        return True
    except LookupError:
        return False


def get_oracle_metadata(
    name: typing.Optional[str] = None,
    *,
    address: typing.Optional[spec.Address] = None,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
    oracle_type: spec.Oracletype = 'feed',
    block: spec.BlockNumberReference = 'latest',
) -> spec.OracleFeedMetadata:
    if oracle_type == 'feed':
        return get_oracle_feed_metadata(
            name=name,
            address=address,
            network=network,
            protocol=protocol,
            block=block,
        )
    else:
        raise Exception('unknown oracle type: ' + str(oracle_type))


def get_oracle_feed_metadata(
    name: typing.Optional[str] = None,
    *,
    address: typing.Optional[spec.Address] = None,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
    block: spec.BlockNumberReference = 'latest',
) -> spec.OracleFeedMetadata:

    # block currently not used

    oracle_feeds = load_oracle_feeds(network=network, protocol=protocol)
    if name is not None:
        return search_utils.get_matching_entry(
            list(oracle_feeds.values()),
            query={'name': name},
        )
    elif address is not None:
        return search_utils.get_matching_entry(
            list(oracle_feeds.values()),
            query={'address': address.lower()},
        )
    else:
        raise Exception('must specify name or address')


#
# # backend functions
#


@toolcache.cache(cachetype='memory')
def load_oracle_feeds(
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
) -> dict[str, spec.OracleFeedMetadata]:
    path = get_oracle_feed_path(network=network, protocol=protocol)
    oracle_feeds = store_utils.load_file_data(path)
    return {oracle_feed['name']: oracle_feed for oracle_feed in oracle_feeds}


def get_oracle_feed_path(
    network: spec.NetworkName = 'mainnet', protocol: str = 'chainlink'
) -> str:
    data_dir = ctc.config.get_data_dir()
    return os.path.join(data_dir, network, 'oracle_feeds', protocol + '.csv')

