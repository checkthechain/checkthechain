from __future__ import annotations

import sys
import typing

import ctc
from ctc import spec
from .. import config_defaults


def upgrade_config(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[str, typing.Any]:
    """upgrade config to latest version as much as possible"""

    # detect version
    version = old_config.get('config_spec_version')
    if version is None:
        version = old_config.get('version')

    # perform upgrade
    if not isinstance(version, str):
        print('old_config has unknown version, using default config', file=sys.stderr)
        return dict(config_defaults.get_default_config())
    if version.startswith('0.2.'):
        return upgrade__0_2_0__to__0_3_0(old_config)
    elif version == '0.3.0':
        return old_config
    else:
        raise spec.ConfigUpgradeError('old_config has unknown version')

    # ? perform validation


def upgrade__0_2_0__to__0_3_0(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:

    upgraded = dict(old_config)
    network_defaults = upgraded.pop('network_defaults', {})
    upgraded['default_network'] = network_defaults.get('default_network')
    upgraded['default_providers'] = network_defaults.get(
        'default_providers', {}
    )

    # add default networks
    upgraded['networks'] = dict(upgraded.get('networks', {}))
    default_networks = config_defaults.get_default_networks_metadata()
    for chain_id, network_metadata in default_networks.items():
        name = network_metadata['name']
        if name not in upgraded['networks']:
            upgraded['networks'][name] = network_metadata

    # convert to integer network references
    chain_ids_by_network_name = {
        network_metadata['name']: network_metadata['chain_id']
        for network_name, network_metadata in upgraded['networks'].items()
    }
    upgraded['networks'] = {
        chain_ids_by_network_name[network_name]: network_metadata
        for network_name, network_metadata in upgraded['networks'].items()
    }

    if upgraded['default_network'] not in chain_ids_by_network_name:
        raise spec.ConfigUpgradeError(
            'unknown chain_id for network ' + str(upgraded['default_network'])
        )
    upgraded['default_network'] = chain_ids_by_network_name[
        upgraded['default_network']
    ]
    upgraded['default_providers'] = {
        chain_ids_by_network_name[network_name]: provider_name
        for network_name, provider_name in upgraded['default_providers'].items()
    }

    # set provider network references to chain_id's instead of network names
    new_providers = {}
    for provider_name, provider in upgraded['providers'].items():
        new_providers[provider_name] = dict(provider)
        old_network = new_providers[provider_name].get('network')
        if isinstance(old_network, str):
            new_providers[provider_name]['network'] = chain_ids_by_network_name[
                old_network
            ]
    upgraded['providers'] = new_providers

    # set db config
    default_db_config = config_defaults.get_default_db_config(
        data_dir=old_config['data_dir']
    )
    upgraded['db_configs'] = {'main': default_db_config}

    # get version
    if 'version' in upgraded:
        del upgraded['version']
    new_version = ctc.__version__

    # strip extra versioning data
    new_version = omit_extra_version_data(new_version)

    # set version
    upgraded['config_spec_version'] = new_version

    return upgraded


def omit_extra_version_data(version: str) -> str:
    for substr in ['a', 'b', 'rc']:
        if substr in version:
            index = version.index(substr)
            version = version[:index]
    return version
