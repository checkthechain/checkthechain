"""utilitize for config file IO"""

from __future__ import annotations

import typing
import warnings
from typing_extensions import TypedDict

import toolconfig

from ctc import spec
from . import config_spec


class _ToolconfigKwargs(TypedDict):
    config_path_env_var: str
    default_config_path: str


_kwargs: _ToolconfigKwargs = {
    'config_path_env_var': config_spec.config_path_env_var,
    'default_config_path': config_spec.default_config_path,
}


def get_config_path(*, raise_if_dne: bool = True) -> str:
    return toolconfig.get_config_path(raise_if_dne=raise_if_dne, **_kwargs)


def config_path_exists() -> bool:
    return toolconfig.config_path_exists(**_kwargs)


@typing.overload
def get_config(validate: typing.Literal['raise'] = 'raise') -> spec.ConfigSpec:
    ...


@typing.overload
def get_config(
    validate: typing.Literal['warn', False]
) -> typing.MutableMapping:
    ...


def get_config(
    validate: toolconfig.ValidationOption = False,
) -> typing.Union[spec.ConfigSpec, typing.MutableMapping]:

    config = toolconfig.get_config(
        config_spec=spec.ConfigSpec, validate=validate, **_kwargs
    )

    version = get_config_version_tuple(config)
    if version < config_spec.min_allowed_config_version:
        raise Exception(
            'config version is too old. upgrade by running `ctc setup` in a terminal'
        )
    if version < config_spec.min_recommended_config_version:
        import rich.console

        warning_text = '[ctc] old config format, upgrade by running `ctc setup` in a terminal'
        warning_text = '[yellow]' + warning_text + '[/yellow]'
        console = rich.console.Console()
        console.print(warning_text)

    validation = validate_config(config)
    # if not validation['valid']:
    # disable validation until 0.3.0 and better upgrade utility in place
    if False:
        warning_text = (
            '\n** ATTENTION **\nctc config is not formatted correctly'
        )
        if len(validation['missing_keys']) > 0:
            warning_text += '\n    missing keys: ' + ', '.join(
                str(key) for key in validation['missing_keys']
            )
        if len(validation['extra_keys']) > 0:
            warning_text += '\n    extra keys: ' + ', '.join(
                str(key) for key in validation['extra_keys']
            )
        warning_text += '\nview more config info by running `[#64aaaa]ctc config[/#64aaaa]` in terminal'
        warning_text += (
            '\nfix config by running `[#64aaaa]ctc setup[/#64aaaa]` in terminal'
        )
        warning_text += '\n'

        import rich.console

        warning_text = '[yellow]' + warning_text + '[/yellow]'
        console = rich.console.Console()
        console.print(warning_text)

    if validate == 'raise':
        return typing.cast(spec.ConfigSpec, config)
    else:
        return config


def get_config_version_tuple(
    config: typing.Mapping,
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


class ConfigValidation(TypedDict):
    valid: bool
    missing_keys: typing.Iterable[str]
    extra_keys: typing.Iterable[str]


def validate_config(config: typing.Mapping) -> ConfigValidation:
    spec_keys = set(spec.ConfigSpec.__annotations__)
    actual_keys = set(config.keys())
    missing_keys = spec_keys - actual_keys
    extra_keys = actual_keys - spec_keys
    valid = spec_keys == actual_keys
    return {
        'valid': valid,
        'missing_keys': missing_keys,
        'extra_keys': extra_keys,
    }


def config_is_valid() -> bool:
    return toolconfig.config_is_valid(config_spec=spec.ConfigSpec, **_kwargs)
