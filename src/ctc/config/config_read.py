from __future__ import annotations

import typing
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
    validate: toolconfig.ValidationOption = 'raise',
) -> typing.Union[spec.ConfigSpec, typing.MutableMapping]:

    config = toolconfig.get_config(
        config_spec=spec.ConfigSpec, validate=validate, **_kwargs
    )
    if validate == 'raise':
        return typing.cast(spec.ConfigSpec, config)
    else:
        return config


def config_is_valid() -> bool:
    return toolconfig.config_is_valid(config_spec=spec.ConfigSpec, **_kwargs)

