"""the goal of these functions is to return the state of the ctc configuration

these functions should
- allow user data to be somewhat malformed
    - assume types are proper
    - some values might be missing
    - str values might be invalid
- return a default when appropriate if no config value is specified
"""

from __future__ import annotations

import typing
import os

if typing.TYPE_CHECKING:
    import toolcli
    import toolsql
    import toolstr

from ctc import spec
from . import config_defaults
from . import config_read


def get_config_spec_version() -> str | None:
    return config_read.get_config().get('config_spec_version')


def get_data_dir() -> str:
    data_dir = config_read.get_config().get('data_dir')
    if data_dir is not None:
        data_dir = os.path.expanduser(data_dir)
        return data_dir
    else:
        return config_defaults.get_default_data_dir()


#
# # networks
#


def get_default_network() -> spec.ChainId:
    return config_read.get_config()['default_network']


def get_config_networks() -> typing.Mapping[spec.ChainId, spec.NetworkMetadata]:
    config = config_read.get_config()
    networks = config.get('networks')
    if networks is not None:
        return networks
    else:
        return config_defaults.get_default_networks_metadata()


def get_networks_that_have_providers() -> typing.Sequence[spec.ChainId]:
    providers = get_providers()
    all_networks = get_config_networks()
    network_set: set[spec.ChainId] = set()
    for provider in providers.values():
        network = provider.get('network')
        if network is not None:

            # convert chain_id to name
            if isinstance(network, str):
                for chain_id, network_metadata in all_networks.items():
                    if network == network_metadata.get('name'):
                        network_set.add(chain_id)
                        break
                else:
                    raise Exception('unknown network name: ' + str(network))

            # add network
            if isinstance(network, int):
                network_set.add(network)
            else:
                raise Exception('unknown network specification')

    return sorted(network for network in network_set)


#
# # providers
#


def get_providers() -> typing.Mapping[spec.NetworkName, spec.Provider]:
    return config_read.get_config()['providers']


def get_network_default_provider(
    network: spec.NetworkName | spec.ChainId,
) -> spec.Provider | None:
    """get default provider for network"""

    if not isinstance(network, int):
        if isinstance(network, str):
            for chain_id, network_metadata in get_config_networks().items():
                if network == network_metadata['name']:
                    network = chain_id
                    break
            else:
                raise Exception('unknown network name: ' + str(type(network)))
        else:
            raise Exception('unknown network type: ' + str(type(network)))

    # get provider of network
    config = config_read.get_config()
    default_providers = config.get('default_providers', {})
    if network in default_providers:
        provider_name = default_providers[network]
        return config['providers'][provider_name]
    else:
        message = 'no default provider specified for network ' + str(network)
        raise Exception(message)


#
# # caches
#

def get_context_cache_rules() -> typing.Sequence[spec.ContextCacheRule]:
    config = config_read.get_config()
    return config['context_cache_rules']


#
# # db
#

def get_db_config(backend_name: str) -> toolsql.DBConfig:
    config = config_read.get_config()
    db_config = config['db_configs'].get(backend_name)
    if db_config is None:
        raise Exception('no valid db_config for ' + str(backend_name))
    return db_config


def get_cache_backends() -> typing.Sequence[str]:
    config = config_read.get_config()
    return list(config['db_configs'].keys())


#
# # logging
#


def get_log_rpc_calls() -> bool:
    config = config_read.get_config()
    return config.get('log_rpc_calls', False)


def get_log_sql_queries() -> bool:
    config = config_read.get_config()
    return config.get('log_sql_queries', False)


def get_log_dir() -> str:
    return os.path.join(get_data_dir(), 'logs')


def get_rpc_requests_log_path() -> str:
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, 'rpc_requests.log')


def get_sql_queries_log_path() -> str:
    log_dir = get_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, 'sql_queries.log')


#
# # cli
#


def get_cli_color_theme() -> toolcli.StyleTheme:
    config = config_read.get_config()
    return config['cli_color_theme']


def get_cli_chart_charset() -> toolstr.SampleMode:
    config = config_read.get_config()
    return config['cli_chart_charset']

