import typing
from typing_extensions import TypedDict, Literal

from . import network_types


RpcSingularRequest = typing.Dict[str, typing.Any]
RpcPluralRequest = typing.List[RpcSingularRequest]
RpcRequest = typing.Union[RpcSingularRequest, RpcPluralRequest]


class RpcSingularResponseRaw(TypedDict):
    id: str
    jsonrpc: str
    result: typing.Any


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
    network: typing.Optional[network_types.NetworkName]
    protocol: Literal['http', 'wss', 'ipc']
    session_kwargs: typing.Optional[dict]
    chunk_size: typing.Optional[int]


class Provider(TypedDict, total=True):
    url: str
    name: typing.Optional[ProviderName]
    network: typing.Optional[network_types.NetworkName]
    protocol: Literal['http', 'wss', 'ipc']
    session_kwargs: typing.Optional[dict]
    chunk_size: typing.Optional[int]


provider_keys = [
    'url',
    'name',
    'network',
    'protocol',
    'session_kwargs',
    'chunk_size',
]

ProviderShortcut = str
ProviderSpec = typing.Union[ProviderShortcut, PartialProvider, Provider, None]
ProviderKey = typing.Tuple[
    int, str, typing.Tuple[typing.Tuple[typing.Any, typing.Any], ...]
]

