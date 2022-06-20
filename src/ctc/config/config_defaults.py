"""
these functions are not imported by default
- end users should never need to use these functions
"""

from __future__ import annotations

import os
import typing

import ctc
from ctc import spec

if typing.TYPE_CHECKING:
    import toolsql


def get_default_config() -> spec.ConfigSpec:
    return {
        'config_spec_version': ctc.__version__,
        'data_dir': get_default_data_dir(),
        #
        # networks
        'default_network': None,
        'networks': get_default_networks_metadata(),
        #
        # providers
        'providers': {},
        'default_providers': {},
        #
        # db
        'db_configs': {},
        #
        # logging
        'log_rpc_calls': get_default_log_rpc_calls(),
        'log_sql_queries': get_default_log_sql_queries(),
    }


def get_default_data_dir() -> str:
    return os.path.abspath(os.path.join(os.path.expanduser('~'), 'ctc_data'))


#
# # networks
#


def get_default_network_names_by_chain_id() -> typing.Mapping[int, str]:
    return {
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


def get_default_chain_ids_by_network_name() -> typing.Mapping[str, int]:
    return {
        name: chain_id
        for chain_id, name in get_default_network_names_by_chain_id().items()
    }


def get_default_block_explorers() -> typing.Mapping[str, str]:
    return {
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


def get_default_networks_metadata() -> typing.Mapping[
    spec.ChainId, spec.NetworkMetadata
]:
    block_explorers = get_default_block_explorers()
    chain_ids_by_network_name = get_default_chain_ids_by_network_name()
    return {
        chain_id: {
            'name': network_name,
            'chain_id': chain_id,
            'block_explorer': block_explorers[network_name],
        }
        for network_name, chain_id in chain_ids_by_network_name.items()
    }


#
# # db
#

def get_default_db_config(data_dir: str) -> toolsql.DBConfig:
    return {
        'dbms': 'sqlite',
        'path': os.path.join(data_dir, 'dbs/ctc.db'),
    }


#
# # logging
#

def get_default_log_rpc_calls() -> bool:
    return False


def get_default_log_sql_queries() -> bool:
    return False
