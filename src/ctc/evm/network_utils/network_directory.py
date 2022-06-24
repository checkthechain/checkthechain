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


@typing.overload
def get_network_name(
    network: spec.NetworkName | int, require: typing.Literal[True]
) -> spec.NetworkName:
    ...


@typing.overload
def get_network_name(
    network: spec.NetworkName | int, require: bool = True
) -> spec.NetworkName | None:
    ...


def get_network_name(
    network: spec.NetworkName | int, require: bool = True
) -> spec.NetworkName | None:

    if isinstance(network, str):
        return network

    config_network_names_by_id = get_network_names_by_chain_id()
    if network in config_network_names_by_id:
        name = config_network_names_by_id[network]
        if name is None:
            if require:
                raise Exception('network name is not known')
            else:
                return name
        elif isinstance(name, str):
            return name
        else:
            raise Exception('bad type for name: ' + str(type(name)))
    else:
        raise Exception('unknown network: ' + str(network))


def get_network_chain_id(network: spec.NetworkName | int) -> spec.ChainId:

    if isinstance(network, int):
        return network

    config_chain_ids_by_network_name = get_chain_ids_by_network_name()
    if network in config_chain_ids_by_network_name:
        return config_chain_ids_by_network_name[network]
    else:
        raise Exception('unknown network: ' + str(network))


def get_chain_ids_by_network_name() -> typing.Mapping[spec.NetworkName, int]:
    return {
        network_metadata['name']: chain_id
        for chain_id, network_metadata in config.get_networks().items()
        if network_metadata['name'] is not None
    }


def get_network_names_by_chain_id() -> typing.Mapping[
    int, spec.NetworkName | None
]:
    return {
        chain_id: network_metadata['name']
        for chain_id, network_metadata in config.get_networks().items()
    }


def get_network_metadata(
    network: spec.NetworkReference,
) -> spec.NetworkMetadata:

    if isinstance(network, str):
        network = get_network_chain_id(network)

    networks = config.get_networks()
    if network in networks:
        return networks[network]
    else:
        raise Exception('unknown network: ' + str(network))


def get_network_block_explorer(network: spec.NetworkReference) -> str | None:
    network_metadata = get_network_metadata(network)
    return network_metadata['block_explorer']
