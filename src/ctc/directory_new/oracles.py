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
):
    if oracle_type == 'feed':
        oracle = get_oracle_feed_metadata(
            name=name,
            network=network,
            protocol=protocol,
        )
        return oracle['address']
    else:
        raise Exception('unknown oracle type: ' + str(oracle_type))


def get_oracle_metadata(
    name: typing.Optional[str] = None,
    *,
    address: typing.Optional[spec.Address] = None,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
) -> spec.OracleFeedMetadata:
    return get_oracle_feed_metadata(
        name=name,
        address=address,
        network=network,
        protocol=protocol,
    )


def get_oracle_feed_metadata(
    name: typing.Optional[str] = None,
    *,
    address: typing.Optional[spec.Address] = None,
    network: spec.NetworkName = 'mainnet',
    protocol: str = 'chainlink',
) -> spec.OracleFeedMetadata:

    oracle_feeds = load_oracle_feeds(network=network, protocol=protocol)
    if name is not None:
        return search_utils.get_matching_entry(
            list(oracle_feeds.values()), name=name
        )
    elif address is not None:
        return search_utils.get_matching_entry(
            list(oracle_feeds.values()), address=address.lower()
        )
    else:
        raise Exception('must specify name or address')


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

