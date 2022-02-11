"""

## Resources
for overview of different chains see
- https://github.com/ethereum-lists/chains
- https://chainlist.org/
"""

from __future__ import annotations

import os

from ctc import config
from ctc import spec
from ctc.toolbox import search_utils
from ctc.toolbox import store_utils


def get_network_name(network: spec.NetworkReference) -> spec.NetworkName:
    return get_network_metadata(network=network)['name']


def get_network_chain_id(network: spec.NetworkReference) -> spec.NetworkId:
    return get_network_metadata(network=network)['chain_id']


def get_network_metadata(
    network: spec.NetworkReference,
) -> spec.NetworkMetadata:

    default_network_data = load_networks_from_disk()
    config_network_data = config.get_networks()
    all_network_data = dict(default_network_data, **config_network_data)
    network_list = list(all_network_data.values())

    if network is None:
        network = config.get_default_network()

    if isinstance(network, int):
        return search_utils.get_matching_entry(
            sequence=network_list,
            query={'chain_id': network},
        )

    elif isinstance(network, str):
        return search_utils.get_matching_entry(
            sequence=network_list,
            query={'name': network},
        )

    else:
        raise Exception('unknown network format: ' + str(network))


def get_networks() -> dict[spec.NetworkName, spec.NetworkMetadata]:
    # use filesystem backend for now
    return load_networks_from_disk()


#
# # filesystem backend
#


def load_networks_from_disk(
    use_default: bool = False,
) -> dict[spec.NetworkName, spec.NetworkMetadata]:
    path = get_networks_file_path(use_default=use_default)
    raw_data = store_utils.load_file_data(path)
    return {network['name']: network for network in raw_data}


def get_networks_file_path(use_default: bool = False) -> str:
    if use_default:
        data_root = config.get_default_data_dir()
    else:
        data_root = config.get_data_dir()
    return os.path.join(data_root, 'networks.csv')

