from __future__ import annotations

import os
import typing

import ctc
from ctc import spec

import toolconfig
import toolcli

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
        return {}

    # upgrade config file if need be
    if (
        convert_to_latest
        and old_config['config_spec_version'] != ctc.__version__
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
) -> None:

    import json

    config_path = config_read.get_config_path(raise_if_dne=False)

    version = upgrade_utils.omit_extra_version_data(ctc.__version__)

    config: spec.Config = {
        'config_spec_version': version,
        'data_dir': data_dir_data['data_dir'],
        'networks': network_data['networks'],
        'providers': network_data['providers'],
        'default_network': network_data['default_network'],
        'default_providers': network_data['default_providers'],
        'db_configs': db_data['db_configs'],
        'log_rpc_calls': data_dir_data['log_rpc_calls'],
        'log_sql_queries': data_dir_data['log_sql_queries'],
    }
    old_config_raw = load_old_config(convert_to_latest=False)
    write_new = json.dumps(config, sort_keys=True) != json.dumps(
        old_config_raw, sort_keys=True
    )

    print()
    print()
    toolcli.print('## Creating Configuration File', style=styles['header'])
    print()
    if write_new:
        with open(config_path, 'w') as f:
            json.dump(config, f)
        toolcli.print(
            'Config file created at',
            toolcli.add_style(config_path, styles['path']),
        )
    else:
        print('Config unchanged')
