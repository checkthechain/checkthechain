"""
these functions are not imported by default
- end users should never need to use these functions
"""

from __future__ import annotations

import os
import typing

import ctc
from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING:
    import toolsql


def get_default_config(use_env_variables: bool = True) -> spec.Config:

    data_dir = get_default_data_dir()

    default_config: spec.Config = {
        'config_spec_version': ctc.__version__,
        'data_dir': data_dir,
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
        'db_configs': get_default_db_configs(data_dir=data_dir),
        #
        # logging
        'log_rpc_calls': get_default_log_rpc_calls(),
        'log_sql_queries': get_default_log_sql_queries(),
    }
    # add in ETH_RPC_URL provider for no config mode
    if use_env_variables:
        add_env_var_rpc_provider(default_config)

    return default_config


def add_env_var_rpc_provider(default_config: spec.Config) -> None:
    eth_rpc_url = os.environ.get('ETH_RPC_URL')
    if eth_rpc_url is not None:
        print('using RPC provider stored in ETH_RPC_URL')
        provider_name = 'ETH_RPC_URL'

        # get chain id either 1) from env or 2) by querying node
        chain_id: int | str | None = os.environ.get('ETH_RPC_CHAIN_ID')
        if chain_id not in [None, '']:
            try:
                chain_id = int(chain_id)  # type: ignore
            except Exception:
                pass
        if chain_id is None:
            try:
                chain_id = _sync_get_chain_id(eth_rpc_url)
            except Exception:
                print(
                    '[WARNING] not using value in ETH_RPC_URL because could not determine its chain_id (value = '
                    + str(eth_rpc_url)
                    + ')'
                )
                return
        if chain_id not in default_config['networks']:
            raise Exception(
                'cannot use provider in ETH_RPC_URL because it uses unknown chain_id = '
                + str(chain_id)
            )

        if not isinstance(chain_id, int) and chain_id is not None:
            raise Exception('could not determine proper value of chain_id')

        default_config['default_network'] = chain_id
        default_config['providers'][provider_name] = {  # type: ignore
            'name': provider_name,
            'network': chain_id,
            'protocol': 'http',
            'url': eth_rpc_url,
            'session_kwargs': {},
            'chunk_size': None,
        }
        default_config['default_providers'][chain_id] = provider_name  # type: ignore


def _sync_get_chain_id(provider_url: str) -> int:
    import json
    import urllib.request

    data = {'jsonrpc': '2.0', 'method': 'eth_chainId', 'params': [], 'id': 1}
    encoded_data = json.dumps(data).encode()
    request = urllib.request.Request(
        provider_url,
        data=encoded_data,
        headers={'User-Agent': 'python3'},
    )
    response = urllib.request.urlopen(request)
    response_data = json.loads(response.read().decode())
    raw_chain_id = response_data['result']
    return evm.binary_convert(raw_chain_id, 'integer')


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
        10: 'optimism',
        42: 'kovan',
        56: 'bnb',
        69: 'optimism_kovan',
        97: 'bnb_testnet',
        100: 'gnosis',
        128: 'heco',
        137: 'polygon',
        250: 'fantom',
        420: 'optimism_goerli',
        1088: 'metis',
        1284: 'moonbeam',
        1285: 'moonriver',
        4002: 'fantom_testnet',
        8217: 'klaytn',
        42161: 'arbitrum',
        43114: 'avalanche',
        43113: 'avalanche_fuji',
        80001: 'polygon_mumbai',
        421611: 'arbitrum_rinkeby',
        1666600000: 'harmony',
        1666700000: 'harmony_testnet',
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
        'optimism': 'optimistic.etherscan.io',
        'kovan': 'kovan.etherscan.io',
        'bnb': 'bscscan.com',
        'optimism_kovan': 'kovan-optimistic.etherscan.io',
        'bnb_testnet': 'testnet.bscscan.com',
        'gnosis': 'blockscout.com',
        'heco': 'hecoinfo.com',
        'polygon': 'polygonscan.com',
        'fantom': 'ftmscan.com',
        'optimism_goerli': 'blockscout.com/optimism/goerli',
        'metis': 'andromeda-explorer.metis.io',
        'moonbeam': 'moonbeam.moonscan.io',
        'moonriver': 'moonriver.moonscan.io',
        'fantom_testnet': 'testnet.ftmscan.com',
        'klaytn': 'scope.klaytn.com',
        'arbitrum': 'arbiscan.io',
        'avalanche': 'snowtrace.io',
        'avalanche_fuji': 'testnet.snowtrace.io',
        'polygon_mumbai': 'mumbai.polygonscan.com',
        'arbitrum_rinkeby': 'testnet.arbiscan.io',
        'harmony': 'explorer.harmony.one',
        'harmony_testnet': 'explorer.testnet.harmony.one',
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


def get_default_db_configs(
    data_dir: str,
) -> typing.Mapping[str, toolsql.DBConfig]:
    return {'main': get_default_db_config(data_dir=data_dir)}


#
# # logging
#


def get_default_log_rpc_calls() -> bool:
    return False


def get_default_log_sql_queries() -> bool:
    return False
