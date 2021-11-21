import typing


RpcSingularRequest = dict[str, typing.Any]
RpcPluralRequest = list[RpcSingularRequest]
RpcRequest = typing.Union[RpcSingularRequest, RpcPluralRequest]


RpcSingularResponse = typing.Any
RpcPluralResponse = list[RpcSingularResponse]
RpcResponse = typing.Union[RpcPluralResponse, RpcSingularResponse]

RpcConstructor = typing.Callable[..., RpcSingularRequest]
RpcDigestor = typing.Callable[..., RpcResponse]


class Provider(typing.TypedDict):
    type: str
    url: str
    session_kwargs: dict


ProviderShortcut = str
ProviderSpec = typing.Union[Provider, ProviderShortcut, None]
ProviderKey = tuple[int, str, tuple[tuple[typing.Any, typing.Any], ...]]

