from __future__ import annotations


class ConfigUpgradeError(Exception):
    pass


class ConfigInvalid(ValueError):
    pass


class ConfigDoesNotExist(FileNotFoundError):
    pass


class ConfigPathNotSet(Exception):
    pass

