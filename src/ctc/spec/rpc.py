import typing


SingularRequestData = dict[str, typing.Any]
PluralRequestData = list[SingularRequestData]
RequestData = typing.Union[SingularRequestData, PluralRequestData]


# class RawRequestData(typing.TypedDict):
#     jsonrpc: str
#     method: str
#     params: list[typing.Any]


SingularResponseData = dict[str, typing.Any]
PluralResponseData = list[SingularResponseData]
ResponseData = typing.Union[SingularResponseData, PluralResponseData]


class Provider(typing.TypedDict):
    type: str
    url: str
    session_kwargs: dict


ProviderShortcut = str
ProviderSpec = typing.Union[Provider, ProviderShortcut]
ProviderKey = tuple[int, str, tuple[tuple[typing.Any, typing.Any], ...]]

