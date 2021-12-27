import toolconfig

from ctc import spec
from . import config_spec


def get_config_path(
    raise_if_unset: bool = True, raise_if_dne: bool = True
) -> str:
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

