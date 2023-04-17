from __future__ import annotations

import json
import os
import typing

import toolcli
import toolstr

import ctc
import ctc.config
from ctc import spec
from ctc.cli import cli_utils
from .. import config_spec
from .. import config_read
from .. import upgrade_utils


def load_old_config(
    convert_to_latest: bool,
) -> typing.Mapping[typing.Any, typing.Any]:

    # get old config path
    config_path: str | None = os.environ.get(config_spec.config_path_env_var)
    if config_path in ['', None]:
        config_path = config_spec.default_config_path

    # load old config file
    if isinstance(config_path, str) and os.path.isfile(config_path):
        with open(config_path) as f:
            old_config: typing.Mapping[typing.Any, typing.Any] = json.load(f)
    else:
        old_config = {}

    old_providers = old_config.get('providers')
    if old_providers is not None:
        for provider_name, provider in list(old_providers.items()):
            for provider_key in spec.provider_keys:
                if provider_key not in provider:
                    if provider_key in spec.default_provider_settings:
                        provider.setdefault(
                            provider_key,
                            spec.default_provider_settings[provider_key],
                        )
                    else:
                        print('skipping provider, missing essential keys')
                        del old_providers[provider_name]

    # upgrade config file if need be
    config_version = old_config.get('config_spec_version')
    if config_version is not None:
        config_stable_version = upgrade_utils.get_stable_version(config_version)
    else:
        config_stable_version = None
    ctc_stable_version = upgrade_utils.get_stable_version(ctc.__version__)
    if convert_to_latest and config_stable_version != ctc_stable_version:
        try:
            old_config = upgrade_utils.upgrade_config(old_config)
        except spec.ConfigUpgradeError:
            print()
            print('old config could not be processed, skipping it')
            old_config = {}

    return old_config


def setup_config_path() -> None:

    # create parent dir
    config_path = config_read.get_config_path(raise_if_dne=False)
    parent_dir = os.path.dirname(config_path)
    os.makedirs(parent_dir, exist_ok=True)


def write_new_config(
    *,
    network_data: spec.PartialConfig,
    db_data: spec.PartialConfig,
    data_dir_data: spec.PartialConfig,
    cli_data: spec.PartialConfig,
    styles: toolcli.StyleTheme,
    overwrite: bool = False,
    headless: bool = False,
) -> None:

    import json

    config_path = config_read.get_config_path(raise_if_dne=False)

    networks = {
        str(key): value for key, value in network_data['networks'].items()
    }
    default_providers = {
        str(key): value
        for key, value in network_data['default_providers'].items()
    }

    config: spec.JsonConfig = {
        'config_spec_version': ctc.__version__,
        'data_dir': data_dir_data['data_dir'],
        'networks': networks,
        'providers': network_data['providers'],
        'default_network': network_data['default_network'],
        'default_providers': default_providers,
        'db_configs': db_data['db_configs'],
        'log_rpc_calls': data_dir_data['log_rpc_calls'],
        'log_sql_queries': data_dir_data['log_sql_queries'],
        'cli_color_theme': cli_data['cli_color_theme'],
        'cli_chart_charset': cli_data['cli_chart_charset'],
        'context_cache_rules': [
            {
                'backend': 'main',
                'read': True,
                'write': True,
            }
        ],
    }
    print()
    print()
    toolstr.print('## Creating Configuration File', style=styles['title'])
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            old_config_raw = json.load(f)
        write_new = json.dumps(config, sort_keys=True) != json.dumps(
            old_config_raw, sort_keys=True
        )

        # print updated keys
        if write_new:

            # detect updated keys
            changed_keys: set[str] = set()
            for key, value in config.items():
                if json.dumps(value, sort_keys=True) != json.dumps(
                    old_config_raw.get(key), sort_keys=True
                ):
                    changed_keys.add(key)
            for key in old_config_raw.keys():
                if key not in config:
                    changed_keys.add(key)

            print()
            if changed_keys == set(config.keys()):
                print('All keys updated')
            else:
                print('Updated keys:')
                for key in sorted(changed_keys):
                    cli_utils.print_bullet(
                        value=key, key_style=styles['description']
                    )
                    old_value = old_config_raw.get(key)
                    new_value = config.get(key)
                    if isinstance(old_value, dict) and isinstance(
                        new_value, dict
                    ):
                        changed_values = {}
                        for k, v in new_value.items():
                            if v != old_value.get(k):
                                changed_values[k] = (old_value.get(k), v)
                        if len(changed_values) > 0:
                            for k, (old_v, new_v) in changed_values.items():
                                cli_utils.print_bullet(
                                    key='subkey', value=k, indent=4
                                )
                                cli_utils.print_bullet(
                                    key='old', value=old_v, indent=8
                                )
                                cli_utils.print_bullet(
                                    key='new', value=new_v, indent=8
                                )

                        # print deleted keys
                        deleted_keys = [
                            k for k in old_value if k not in new_value
                        ]
                        if len(deleted_keys) > 0:
                            print('    - deleted subkeys:', deleted_keys)

                    else:
                        cli_utils.print_bullet(
                            key='old value',
                            value=old_config_raw.get(key),
                            indent=4,
                        )
                        cli_utils.print_bullet(
                            key='new value', value=config.get(key), indent=4
                        )

        # make sure file overwrite is confirmed
        if write_new and not overwrite:
            print()
            if not toolcli.input_yes_or_no(
                'Overwrite old config file? ',
                default='yes',
                style=styles['metavar'],
                headless=headless,
            ):
                raise Exception('cannot continue without replacing config file')
    else:
        write_new = True

    print()
    if write_new:
        with open(config_path, 'w') as f:
            json.dump(config, f)
        toolstr.print(
            'Config file created at',
            toolstr.add_style(config_path, styles['description']),
        )
    else:
        print('Config unchanged')

