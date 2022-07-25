from __future__ import annotations

import os
import typing

import ctc
from ctc import spec

import toolcli
import toolconfig
import toolstr

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
        old_config = toolconfig.load_config_file(config_path)
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
    if (
        convert_to_latest
        and old_config.get('config_spec_version') != ctc.__version__
    ):
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
    styles: typing.Mapping[str, str],
    overwrite: bool = False,
    headless: bool = False,
) -> None:

    import json

    config_path = config_read.get_config_path(raise_if_dne=False)

    version = upgrade_utils.omit_extra_version_data(ctc.__version__)

    networks = {
        str(key): value for key, value in network_data['networks'].items()
    }
    default_providers = {
        str(key): value
        for key, value in network_data['default_providers'].items()
    }

    config: spec.JsonConfig = {
        'config_spec_version': version,
        'data_dir': data_dir_data['data_dir'],
        'networks': networks,
        'providers': network_data['providers'],
        'default_network': network_data['default_network'],
        'default_providers': default_providers,
        'db_configs': db_data['db_configs'],
        'log_rpc_calls': data_dir_data['log_rpc_calls'],
        'log_sql_queries': data_dir_data['log_sql_queries'],
    }
    print()
    print()
    toolstr.print('## Creating Configuration File', style=styles['header'])
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            old_config_raw = json.load(f)
        write_new = json.dumps(config, sort_keys=True) != json.dumps(
            old_config_raw, sort_keys=True
        )

        # make sure file overwrite is confirmed
        if write_new and not overwrite:
            print()
            if not toolcli.input_yes_or_no(
                'Overwrite old config file? ',
                default='yes',
                style=styles['question'],
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
            toolstr.add_style(config_path, styles['path']),
        )
    else:
        print('Config unchanged')
