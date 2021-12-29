import toolconfig

from ctc import spec
from . import config_spec


_kwargs = {
    'config_path_env_var': config_spec.config_path_env_var,
    'default_config_path': config_spec.default_config_path,
}


def get_config_path(*, raise_if_dne: bool = True) -> str:
    return toolconfig.get_config_path(raise_if_dne=raise_if_dne, **_kwargs)


def config_path_exists() -> bool:
    return toolconfig.config_path_exists(**_kwargs)


def get_config(
    validate: toolconfig.ValidationOption = 'raise',
) -> spec.ConfigSpec:

    return toolconfig.get_config(
        config_spec=spec.ConfigSpec, validate=validate, **_kwargs
    )


def config_is_valid() -> bool:
    return toolconfig.config_is_valid(
        config_spec=spec.ConfigSpec,
        **_kwargs
    )

