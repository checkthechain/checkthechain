from __future__ import annotations

import types
import typing

from ctc import spec
from . import rpc_constructors
from . import rpc_digestors


def get_constructors() -> dict[str, spec.RpcConstructor]:
    constructors: dict[str, typing.Callable[..., typing.Any]] = {}
    for key in dir(rpc_constructors):
        if key.startswith('construct_'):
            candidate = getattr(rpc_constructors, key)
            if isinstance(candidate, types.FunctionType):
                constructors[key.split('construct_')[-1]] = candidate
    return constructors


def get_digestors() -> dict[str, spec.RpcDigestor]:
    digestors: dict[str, typing.Callable[..., typing.Any]] = {}
    for key in dir(rpc_digestors):
        if key.startswith('digest_'):
            candidate = getattr(rpc_digestors, key)
            if isinstance(candidate, types.FunctionType):
                digestors[key.split('digest_')[-1]] = candidate
    return digestors


def get_constructor(method: str) -> spec.RpcConstructor:
    return get_constructors()[method]


def get_digestor(method: str) -> spec.RpcDigestor:
    return get_digestors()[method]
