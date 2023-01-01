"""utilitize for config file IO"""

from __future__ import annotations

import functools
import sys
import typing
from typing_extensions import TypedDict

if typing.TYPE_CHECKING:
    import toolconfig

import ctc
from ctc import spec
from . import config_env_vars
from . import config_overrides
from . import config_spec
from . import config_validate
from . import upgrade_utils


class _ToolconfigKwargs(TypedDict):
    config_path_env_var: str
    default_config_path: str


_kwargs: _ToolconfigKwargs = {
    'config_path_env_var': config_spec.config_path_env_var,
    'default_config_path': config_spec.default_config_path,
}


def get_config_path(*, raise_if_dne: bool = True) -> str:
    import toolconfig

    return toolconfig.get_config_path(raise_if_dne=raise_if_dne, **_kwargs)


def config_path_exists() -> bool:
    import toolconfig

    return toolconfig.config_path_exists(**_kwargs)


@typing.overload
def get_config(
    validate: typing.Literal['raise'] = 'raise',
    warn_if_dne: bool = True,
) -> spec.Config:
    ...


@typing.overload
def get_config(
    validate: typing.Literal['warn', False],
    warn_if_dne: bool = True,
) -> typing.MutableMapping[str, typing.Any]:
    ...


@functools.lru_cache()
def get_config(
    validate: toolconfig.ValidationOption = False,
    warn_if_dne: bool = True,
    warn_if_outdated: bool = True,
) -> typing.Union[spec.Config, typing.MutableMapping[str, typing.Any]]:

    import toolconfig

    # load from file
    try:
        raw_config = toolconfig.get_config(
            config_spec=None, validate=validate, **_kwargs
        )
    except toolconfig.ConfigDoesNotExist:
        from . import config_defaults

        if warn_if_dne:
            print(
                '[WARNING]'
                ' ctc config file does not exist;'
                ' use `ctc setup` on command line to generate a config file',
                file=sys.stderr,
            )
        raw_config = config_defaults.get_default_config(
            use_env_variables=True,
        )  # type: ignore

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

    if validate == 'raise':
        if typing.TYPE_CHECKING:
            return typing.cast(spec.Config, raw_config)
        else:
            return raw_config
    else:
        return raw_config


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
    for cache_function in _get_config_cache_functions():
        cache_function.cache_clear()


def _get_config_cache_functions() -> typing.Sequence[
    functools._lru_cache_wrapper[typing.Any]
]:
    return [
        get_config,  # type: ignore
    ]

