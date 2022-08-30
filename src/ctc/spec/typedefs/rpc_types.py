"""
## Next type system for RPC requests/responses
- create RpcRequest[Method] and RpcResponse[Method]
- implement using mypy plugin with get_type_analyze_hook()
    - https://github.com/python/mypy/issues/6503
    - https://github.com/python/mypy/issues/8848
"""
from __future__ import annotations

import typing
from typing_extensions import TypedDict, Literal

from . import network_types


RpcSingularRequest = typing.Dict[str, typing.Any]
RpcPluralRequest = typing.List[RpcSingularRequest]
RpcRequest = typing.Union[RpcSingularRequest, RpcPluralRequest]


class RpcSingularResponseSuccess(TypedDict):
    id: str
    jsonrpc: str
    result: typing.Any


class RpcSingularResponseFailure(TypedDict):
    id: str
    jsonrpc: str
    error: typing.Any


RpcSingularResponseRaw = typing.Union[
    RpcSingularResponseSuccess,
    RpcSingularResponseFailure,
]


RpcPluralResponseRaw = typing.List[RpcSingularResponseRaw]
RpcResponseRaw = typing.Union[RpcSingularResponseRaw, RpcPluralResponseRaw]

RpcSingularResponse = typing.Any
RpcPluralResponse = typing.List[RpcSingularResponse]
RpcResponse = typing.Union[RpcPluralResponse, RpcSingularResponse]

RpcConstructor = typing.Callable[..., RpcSingularRequest]
RpcDigestor = typing.Callable[..., RpcResponse]


#
# # provider
#

ProviderName = str


class PartialProvider(TypedDict, total=False):
    url: str
    name: typing.Optional[ProviderName]
    network: typing.Optional[network_types.NetworkReference]
    protocol: Literal['http', 'wss', 'ipc']
    session_kwargs: typing.Optional[dict[str, typing.Any]]
    chunk_size: typing.Optional[int]
    convert_reverts_to_none: bool


class Provider(TypedDict, total=True):
    url: str
    name: typing.Optional[ProviderName]
    network: network_types.NetworkReference
    protocol: Literal['http', 'wss', 'ipc']
    session_kwargs: typing.Optional[dict[str, typing.Any]]
    chunk_size: typing.Optional[int]
    convert_reverts_to_none: bool


ProviderShortcut = str
ProviderReference = typing.Union[
    ProviderShortcut, PartialProvider, Provider, None
]
ProviderKey = typing.Tuple[
    int, str, typing.Tuple[typing.Tuple[typing.Any, typing.Any], ...]
]
