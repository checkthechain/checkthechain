import typing


RpcSingularRequest = dict[str, typing.Any]
RpcPluralRequest = list[RpcSingularRequest]
RpcRequest = typing.Union[RpcSingularRequest, RpcPluralRequest]


class RpcSingularResponseRaw(typing.TypedDict):
    id: str
    jsonrpc: str
    result: typing.Any


RpcPluralResponseRaw = list[RpcSingularResponseRaw]
RpcResponseRaw = typing.Union[RpcSingularResponseRaw, RpcPluralResponseRaw]

RpcSingularResponse = typing.Any
RpcPluralResponse = list[RpcSingularResponse]
RpcResponse = typing.Union[RpcPluralResponse, RpcSingularResponse]

RpcConstructor = typing.Callable[..., RpcSingularRequest]
RpcDigestor = typing.Callable[..., RpcResponse]


#
# # provider
#

ProviderName = str

class PartialProvider(typing.TypedDict, total=False):
    name: ProviderName
    type: str
    url: str
    session_kwargs: dict
    chunk_size: typing.Optional[int]


class Provider(typing.TypedDict, total=True):
    # name: ProviderName
    type: str
    url: str
    session_kwargs: dict
    chunk_size: typing.Optional[int]


ProviderShortcut = str
ProviderSpec = typing.Union[ProviderShortcut, PartialProvider, Provider, None]
ProviderKey = tuple[int, str, typing.Tuple[tuple[typing.Any, typing.Any], ...]]

