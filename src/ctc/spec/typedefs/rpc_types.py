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

ProviderShortcut = str


class PartialProvider(TypedDict, total=False):
    url: str
    name: str | None
    network: network_types.NetworkReference | None
    protocol: Literal['http', 'wss', 'ipc']
    #
    # query behaviors
    session_kwargs: typing.Mapping[str, typing.Any] | None
    chunk_size: int | None
    convert_reverts_to_none: bool
    disable_batch_requests: bool


class Provider(TypedDict, total=True):
    url: str
    name: str | None
    network: network_types.ChainId
    protocol: Literal['http', 'wss', 'ipc']
    #
    # query behaviors
    session_kwargs: typing.Mapping[str, typing.Any] | None
    chunk_size: int | None
    convert_reverts_to_none: bool
    disable_batch_requests: bool


ProviderReference = typing.Union[ProviderShortcut, PartialProvider, Provider]
ProviderId = typing.Tuple[
    int, str, typing.Tuple[typing.Tuple[typing.Any, typing.Any], ...]
]

