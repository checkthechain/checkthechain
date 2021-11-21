import typing


RpcSingularRequest = dict[str, typing.Any]
RpcPluralRequest = list[RpcSingularRequest]
RpcRequest = typing.Union[RpcSingularRequest, RpcPluralRequest]


RpcResponse = typing.Any


class Provider(typing.TypedDict):
    type: str
    url: str
    session_kwargs: dict


ProviderShortcut = str
ProviderSpec = typing.Union[Provider, ProviderShortcut, None]
ProviderKey = tuple[int, str, tuple[tuple[typing.Any, typing.Any], ...]]

