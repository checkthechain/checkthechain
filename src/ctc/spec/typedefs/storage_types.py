from __future__ import annotations

import typing

from typing_extensions import Literal, TypedDict, NotRequired

from . import address_types


StorageBackend = Literal['Filesystem']

FilesystemRoot = Literal['root', 'default']


class DexPool(TypedDict):
    address: address_types.Address
    factory: address_types.Address
    asset0: address_types.Address | None
    asset1: address_types.Address | None
    asset2: NotRequired[address_types.Address | None]
    asset3: NotRequired[address_types.Address | None]
    creation_block: int
    fee: int | None
    additional_data: NotRequired[typing.Mapping[typing.Any, typing.Any]]
    priority: NotRequired[int | None]
