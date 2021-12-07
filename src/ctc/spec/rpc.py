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


class PartialProvider(typing.TypedDict, total=False):
    type: str
    url: str
    session_kwargs: dict
    chunk_size: typing.Optional[int]


class Provider(PartialProvider, total=True):
    type: str
    url: str
    session_kwargs: dict
    chunk_size: typing.Optional[int]


ProviderShortcut = str
ProviderSpec = typing.Union[ProviderShortcut, PartialProvider, Provider, None]
ProviderKey = tuple[int, str, typing.Tuple[tuple[typing.Any, typing.Any], ...]]

