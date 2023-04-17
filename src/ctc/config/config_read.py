"""utilitize for config file IO"""

from __future__ import annotations

import os
import functools
import sys
import typing

import ctc
from ctc import spec
from . import config_env_vars
from . import config_overrides
from . import config_spec
from . import config_validate
from . import upgrade_utils


def get_config_path(*, raise_if_dne: bool = True) -> str:

    config_path_env_var = config_spec.config_path_env_var
    default_config_path = config_spec.default_config_path

    # get config_path from environmental variable
    if config_path_env_var is not None:
        config_path = os.environ.get(config_path_env_var)
        if config_path == '':
            config_path = None

    # use default config path if not specified
    if config_path is None and default_config_path is not None:
        config_path = default_config_path

    # validate config_path
    if config_path is None:
        raise spec.ConfigPathNotSet('config path is not set')
    else:
        if raise_if_dne and not os.path.isfile(config_path):
            raise spec.ConfigDoesNotExist(
                'config at path does not exist: ' + str(config_path)
            )

    return config_path


@functools.lru_cache()
def get_config(
    warn_if_dne: bool = True,
    warn_if_outdated: bool = True,
) -> spec.Config:

    # load from file
    try:
        config_path = get_config_path()
        with open(config_path, 'r') as f:
            import json

            raw_config = json.load(f)
    except spec.ConfigDoesNotExist:
        from . import config_defaults

        if warn_if_dne:
            print(
                '[WARNING]'
                ' ctc config file does not exist;'
                ' use `ctc setup` on command line to generate a config file',
                file=sys.stderr,
            )
        raw_config = config_defaults.get_default_config(use_env_variables=True)

    # auto-upgrade config if need be
    config_version = raw_config.get('config_spec_version')
    if config_version is not None:
        config_stable_version = upgrade_utils.get_stable_version(config_version)
    else:
        config_stable_version = None
    ctc_stable_version = upgrade_utils.get_stable_version(ctc.__version__)
    if config_stable_version != ctc_stable_version:
        if warn_if_outdated:
            print(
                '[WARNING] using outdated config -- run `ctc setup` on command line to update',
                file=sys.stderr,
            )
        raw_config = upgrade_utils.upgrade_config(raw_config)

    # convert int keys from str to int
    for key in spec.typedata.config_int_subkeys:
        if raw_config.get(key) is not None:
            raw_config[key] = {
                int(chain_id): network_metadata
                for chain_id, network_metadata in raw_config[key].items()
            }

    # load settings from env vars
    raw_config = config_env_vars._add_config_env_vars(raw_config)

    # add config overrides
    raw_config = raw_config
    overrides = config_overrides.get_config_overrides()
    if len(overrides) > 0:
        raw_config = dict(raw_config)
        raw_config.update(overrides)

    # validate
    config_validate.validate_config(raw_config)
    return raw_config  # type: ignore


def get_config_version_tuple(
    config: typing.Mapping[str, typing.Any],
) -> typing.Tuple[int, int, int]:

    if 'config_spec_version' in config:
        version_str = config['config_spec_version']
        if isinstance(version_str, str):
            version_tuple = tuple(
                int(token) for token in version_str.split('.')
            )
            if len(version_tuple) == 3:
                return (version_tuple[0], version_tuple[1], version_tuple[2])

    elif 'config_version' in config:
        config_version = config['config_version']
        if (
            isinstance(config_version, list)
            and len(config_version) == 3
            and isinstance(config_version[0], int)
            and isinstance(config_version[1], int)
            and isinstance(config_version[2], int)
        ):
            return (config_version[0], config_version[1], config_version[2])

    raise Exception('could not detect config version')


def reset_config_cache() -> None:
    get_config.cache_clear()

