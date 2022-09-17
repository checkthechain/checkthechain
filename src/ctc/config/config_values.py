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
from typing_extensions import Literal
import os

if typing.TYPE_CHECKING:
    import toolsql

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


def get_default_network() -> spec.ChainId | None:
    return config_read.get_config().get('default_network')


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


def has_provider(
    *,
    name: str | None = None,
    network: str | None = None,
    url: str | None = None,
) -> bool:
    try:
        get_provider(name=name, network=network, url=url)
        return True
    except LookupError:
        return False


def get_provider(
    *,
    name: str | None = None,
    network: str | int | None = None,
    protocol: str | None = None,
    url: str | None = None,
) -> spec.Provider:

    from ctc.toolbox import search_utils

    providers = list(get_providers().values())

    # build query
    query: typing.MutableMapping[str, str | int] = {}
    if name is None and network is None and url is None:
        raise Exception('specify network name or network or url')
    if name is not None:
        query['name'] = name
    if network is not None:
        if isinstance(network, str):
            from ctc import evm

            network = evm.get_network_chain_id(network)
        query['network'] = network
    if protocol is not None:
        query['protocol'] = protocol
    if url is not None:
        query['url'] = url

    return search_utils.get_matching_entry(sequence=providers, query=query)


def get_default_provider(
    network: spec.NetworkName | spec.ChainId | None = None,
) -> spec.Provider:
    """get default provider for network"""

    # if network not specified use default
    if network is None:
        network = get_default_network()
    if network is None:
        raise Exception('no default network specified')

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
        return get_provider(name=default_providers[network])
    else:
        message = 'no default provider specified for network ' + str(network)
        raise Exception(message)


#
# # db
#


@typing.overload
def get_db_config(
    *,
    schema_name: str | None = None,
    network: spec.NetworkReference | None = None,
    require: Literal[True],
) -> 'toolsql.DBConfig':
    ...


@typing.overload
def get_db_config(
    *,
    schema_name: str | None = None,
    network: spec.NetworkReference | None = None,
    require: bool = False,
) -> 'toolsql.DBConfig' | None:
    ...


def get_db_config(
    *,
    schema_name: str | None = None,
    network: spec.NetworkReference | None = None,
    require: bool = False,
) -> 'toolsql.DBConfig' | None:

    # for now, use same database for all schema_names and networks
    config = config_read.get_config()
    db_config = config.get('db_configs', {}).get('main')
    if require and db_config is None:
        raise Exception('db not configured')
    return db_config


#
# # logging
#


def get_log_rpc_calls() -> bool:
    config = config_read.get_config(warn_if_dne=False)
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
