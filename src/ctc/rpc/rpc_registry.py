import types
import typing

from . import rpc_constructors
from . import rpc_digestors


def get_constructors():
    constructors: dict[str, typing.Callable[..., typing.Any]] = {}
    for key in dir(rpc_constructors):
        if key.startswith('construct_'):
            candidate = getattr(rpc_digestors, key)
            if isinstance(candidate, types.FunctionType):
                constructors[key] = candidate
    return constructors


def get_digestors() -> dict[str, typing.Callable]:
    digestors: dict[str, typing.Callable[..., typing.Any]] = {}
    for key in dir(rpc_digestors):
        if key.startswith('digest_'):
            candidate = getattr(rpc_digestors, key)
            if isinstance(candidate, types.FunctionType):
                digestors[key] = candidate
    return digestors

