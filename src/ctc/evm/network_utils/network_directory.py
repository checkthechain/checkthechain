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


default_chain_ids_by_network_name = {
    'mainnet': 1,
    'ropsten': 3,
    'rinkeby': 4,
    'goerli': 5,
    'kovan': 42,
    'polygon': 137,
    'bsc': 56,
    'xdai': 100,
    'avax': 43114,
    'fantom': 250,
    'arbitrum': 42161,
    'optimism': 10,
}


default_network_names_by_chain_id = {
    1: 'mainnet',
    3: 'ropsten',
    4: 'rinkeby',
    5: 'goerli',
    42: 'kovan',
    137: 'polygon',
    57: 'bsc',
    100: 'xdai',
    43114: 'avax',
    250: 'fantom',
    42161: 'arbitrum',
    10: 'optimism',
}


default_block_explorers = {
    'mainnet': 'etherscan.io',
    'ropsten': 'ropsten.etherscan.io',
    'rinkeby': 'rinkeby.etherscan.io',
    'goerli': 'goerli.etherscan.io',
    'kovan': 'kovan.etherscan.io',
    'polygon': 'polygonscan.com',
    'bsc': 'bscscan.com',
    'xdai': 'blockscout.com',
    'avax': 'snowtrace.io',
    'fantom': 'ftmscan.com',
    'arbitrum': 'arbiscan.io',
    'optimism': 'optimistic.etherscan.io',
}


def get_network_name(network: spec.NetworkName | int) -> spec.NetworkName:

    if isinstance(network, str):
        return network

    config_network_names_by_id = config.get_network_names_by_chain_id()
    if network in config_network_names_by_id:
        return config_network_names_by_id[network]
    elif network in default_network_names_by_chain_id:
        return default_network_names_by_chain_id[network]
    else:
        raise Exception('unknown network: ' + str(network))


def get_network_chain_id(network: spec.NetworkName | int) -> spec.NetworkId:

    if isinstance(network, int):
        return network

    config_chain_ids_by_network_name = config.get_chain_ids_by_network_name()
    if network in config_chain_ids_by_network_name:
        return config_chain_ids_by_network_name[network]
    elif network in default_chain_ids_by_network_name:
        return default_chain_ids_by_network_name[network]
    else:
        raise Exception('unknown network: ' + str(network))


def get_network_metadata(
    network: spec.NetworkReference,
) -> spec.NetworkMetadata:
    config_networks = config.get_networks()
    if isinstance(network, str):
        if network in config_networks:
            return config_networks[network]
        elif network in default_chain_ids_by_network_name:
            name = network
            chain_id = default_chain_ids_by_network_name[network]
        else:
            raise Exception('unkown network: ' + str(network))
    elif isinstance(network, int):
        config_networks_by_id = {
            network_metadata['chain_id']: network_metadata
            for network_metadata in config_networks.values()
        }
        if network in config_networks_by_id:
            return config_networks_by_id[network]
        elif network in default_network_names_by_chain_id:
            chain_id = network
            name = default_network_names_by_chain_id[network]
        else:
            raise Exception('unkown network: ' + str(network))

    block_explorer = default_block_explorers.get(name)

    return {
        'name': name,
        'chain_id': chain_id,
        'block_explorer': block_explorer,
    }


def get_default_networks_metadata() -> typing.Mapping[
    str, spec.NetworkMetadata
]:
    return {
        network_name: {
            'name': network_name,
            'chain_id': chain_id,
            'block_explorer': default_block_explorers[network_name],
        }
        for network_name, chain_id in default_chain_ids_by_network_name.items()
    }
