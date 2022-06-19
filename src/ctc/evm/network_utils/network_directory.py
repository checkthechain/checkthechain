"""
## Resources
for overview of different chains see
- https://github.com/ethereum-lists/chains
- https://chainlist.org/
"""

from __future__ import annotations

import typing

from ctc import config
from ctc import spec


def get_network_name(network: spec.NetworkName | int) -> spec.NetworkName:

    if isinstance(network, str):
        return network

    config_network_names_by_id = get_network_names_by_chain_id()
    if network in config_network_names_by_id:
        return config_network_names_by_id[network]
    else:
        raise Exception('unknown network: ' + str(network))


def get_network_chain_id(network: spec.NetworkName | int) -> spec.NetworkId:

    if isinstance(network, int):
        return network

    config_chain_ids_by_network_name = get_chain_ids_by_network_name()
    if network in config_chain_ids_by_network_name:
        return config_chain_ids_by_network_name[network]
    else:
        raise Exception('unknown network: ' + str(network))


def get_chain_ids_by_network_name() -> typing.Mapping[spec.NetworkName, int]:
    return {
        network_name: network_metadata['chain_id']
        for network_name, network_metadata in config.get_networks().items()
    }


def get_network_names_by_chain_id() -> typing.Mapping[int, spec.NetworkName]:
    return {
        network_metadata['chain_id']: network_name
        for network_name, network_metadata in config.get_networks().items()
    }


def get_network_metadata(
    network: spec.NetworkReference,
) -> spec.NetworkMetadata:
    if isinstance(network, int):
        network = get_network_name(network)

    networks = config.get_networks()
    if network in networks:
        return networks[network]
    else:
        raise Exception('unknown network: ' + str(network))
