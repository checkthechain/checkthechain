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


class Provider(typing.TypedDict):
    type: str
    url: str
    session_kwargs: dict
    chunk_size: typing.Optional[int]


ProviderShortcut = str
ProviderSpec = typing.Union[Provider, ProviderShortcut, None]
ProviderKey = tuple[int, str, tuple[tuple[typing.Any, typing.Any], ...]]

