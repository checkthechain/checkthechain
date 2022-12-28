from __future__ import annotations

import typing

from ctc import spec
from . import config_read


_config_overrides: spec.PartialConfig = {}


def set_config_override(key: str, value: typing.Any) -> None:
    _config_overrides[key] = value  # type: ignore
    config_read.reset_config_cache()


def get_config_overrides() -> spec.PartialConfig:
    return _config_overrides


def clear_config_override(key: str) -> None:
    del _config_overrides[key]  # type: ignore
    config_read.reset_config_cache()


def clear_all_config_overrides() -> None:
    for key in list(_config_overrides.keys()):
        del _config_overrides[key]  # type: ignore
    config_read.reset_config_cache()

