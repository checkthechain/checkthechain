import typing

import toolconfig

from ctc import spec
from . import config_spec


@typing.overload
def get_config_path(
    *,
    raise_if_unset: typing.Literal[True] = True,
    raise_if_dne: typing.Literal[True] = True,
) -> str:
    ...


@typing.overload
def get_config_path(
    *,
    raise_if_unset: bool,
    raise_if_dne: bool = True,
) -> typing.Optional[str]:
    ...


@typing.overload
def get_config_path(
    *,
    raise_if_dne: bool,
    raise_if_unset: bool = True,
) -> typing.Optional[str]:
    ...


def get_config_path(
    *, raise_if_unset: bool = True, raise_if_dne: bool = True
) -> typing.Optional[str]:
    return toolconfig.get_config_path(
        config_path_env_var=config_spec.config_path_env_var,
        raise_if_unset=raise_if_unset,
        raise_if_dne=raise_if_dne,
    )


def config_path_exists() -> bool:
    return toolconfig.config_path_exists(
        config_path_env_var=config_spec.config_path_env_var
    )


def config_path_is_set() -> bool:
    return toolconfig.config_path_is_set(
        config_path_env_var=config_spec.config_path_env_var
    )


def get_config() -> spec.ConfigSpec:

    return toolconfig.get_config(
        config_path_env_var=config_spec.config_path_env_var,
        config_spec=spec.ConfigSpec,
        # validate='warn',
        validate='raise',
    )

