from __future__ import annotations

import sys
import typing

import ctc
from ctc import spec
from .. import config_defaults
from . import version_utils


def get_config_upgrade_functions() -> (
    typing.Mapping[
        str,
        typing.Callable[
            [typing.MutableMapping[typing.Any, typing.Any]],
            typing.MutableMapping[typing.Any, typing.Any],
        ],
    ]
):
    return {
        '0.2.': upgrade__0_2_0__to__0_3_0,
        '0.3.0': upgrade__0_3_0__to__0_3_1,
        '0.3.1': upgrade__0_3_1__to__0_3_2,
        '0.3.2': upgrade__0_3_2__to__0_3_3,
        '0.3.3': upgrade__0_3_3__to__0_3_4,
        '0.3.4': upgrade__0_3_4__to__0_3_5,
        '0.3.5': upgrade__0_3_5__to__0_3_6,
    }


def upgrade_config(
    old_config: typing.Mapping[typing.Any, typing.Any]
) -> typing.MutableMapping[str, typing.Any]:
    """upgrade config to latest version as much as possible"""

    import string

    # detect version
    version = old_config.get('config_spec_version')
    if version is None:
        version = old_config.get('version')

    # perform upgrade
    if not isinstance(version, str):
        print(
            'old_config has unknown version, using default config',
            file=sys.stderr,
        )
        return dict(config_defaults.get_default_config())

    new_config: typing.MutableMapping[typing.Any, typing.Any] = dict(old_config)
    config_version = version
    current_version_clean = ctc.__version__.rstrip(string.ascii_letters)
    upgrade_functions = get_config_upgrade_functions()

    # check that current config version is recognized
    if not config_version.startswith(current_version_clean) and not any(
        config_version.startswith(upgrade_version)
        for upgrade_version in upgrade_functions.keys()
    ):
        raise Exception('invalid config version')

    # update config from old version using upgrade path
    for from_version, upgrade_function in upgrade_functions.items():
        if config_version.startswith(from_version):
            new_config = upgrade_function(new_config)
            config_version = new_config['config_spec_version']

    new_config_stable = version_utils.get_stable_version(
        new_config['config_spec_version']
    )
    ctc_stable = version_utils.get_stable_version(ctc.__version__)
    if (
        new_config_stable == ctc_stable
        and new_config['config_spec_version'] != ctc.__version__
    ):
        new_config['config_spec_version'] = ctc.__version__

    return new_config

    # # ? perform validation


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

    upgraded['log_rpc_calls'] = True
    upgraded['log_sql_queries'] = True

    # set new version
    if 'version' in upgraded:
        del upgraded['version']
    upgraded['config_spec_version'] = '0.3.0'

    return upgraded


def upgrade__0_3_0__to__0_3_1(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:
    upgraded = dict(old_config)
    if 'cli_color_theme' not in upgraded:
        upgraded[
            'cli_color_theme'
        ] = config_defaults.get_default_cli_color_theme()
    if 'cli_chart_charset' not in upgraded:
        upgraded[
            'cli_chart_charset'
        ] = config_defaults.get_default_cli_chart_charset()
    upgraded['config_spec_version'] = '0.3.1'

    return upgraded


def upgrade__0_3_1__to__0_3_2(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:
    upgraded = dict(old_config)
    default_config: typing.Mapping[
        str, typing.Any
    ] = config_defaults.get_default_config()
    for key in [
        'context_cache_rules',
    ]:
        if key not in upgraded:
            upgraded[key] = default_config[key]

    if old_config.get('default_network') is None:
        old_config['default_network'] = 1

    upgraded['config_spec_version'] = '0.3.2'

    return upgraded


def upgrade__0_3_2__to__0_3_3(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:
    upgraded = dict(old_config)
    upgraded['config_spec_version'] = '0.3.3'
    return upgraded


def upgrade__0_3_3__to__0_3_4(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:
    upgraded = dict(old_config)
    upgraded['config_spec_version'] = '0.3.4'
    for provider in upgraded['providers'].values():
        provider.setdefault('disable_batch_requests', False)
    for network in upgraded['networks'].values():
        if network['name'] == 'mainnet':
            network['name'] = 'ethereum'
    return upgraded


def upgrade__0_3_4__to__0_3_5(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:
    upgraded = dict(old_config)
    upgraded['config_spec_version'] = '0.3.5'
    return upgraded


def upgrade__0_3_5__to__0_3_6(
    old_config: typing.MutableMapping[typing.Any, typing.Any]
) -> typing.MutableMapping[typing.Any, typing.Any]:
    upgraded = dict(old_config)
    upgraded['config_spec_version'] = '0.3.6'
    return upgraded


def omit_extra_version_data(version: str) -> str:
    for substr in ['a', 'b', 'rc']:
        if substr in version:
            index = version.index(substr)
            version = version[:index]
    return version

