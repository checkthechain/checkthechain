from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import db_types
from . import rpc_types
from . import network_types


class PartialContext(TypedDict, total=False):
    provider: rpc_types.ProviderReference
    network: network_types.NetworkReference
    #
    # cache settings
    cache: bool | CacheId | typing.Mapping[
        db_types.SchemaName,
        bool | CacheId | SingleCacheContext,
    ]
    read_cache: bool
    write_cache: bool


class FullContext(TypedDict):
    provider: rpc_types.Provider
    network: network_types.ChainId
    #
    # cache settings
    cache: MultiCacheContext


# one of: provider url, network name
ContextStr = str

Context = typing.Union[
    PartialContext,
    FullContext,
    ContextStr,
    network_types.ChainId,
]


#
# # cache configuration
#

CacheId = str


class SingleCacheContext(TypedDict):
    cache: CacheId
    read_cache: bool
    write_cache: bool


MultiCacheContext = typing.Mapping[
    db_types.SchemaName,
    SingleCacheContext,
]

MutableMultiCacheContext = typing.MutableMapping[
    db_types.SchemaName,
    SingleCacheContext,
]


class PartialSingleCacheContext(TypedDict, total=False):
    cache: CacheId
    read_cache: bool
    write_cache: bool


PartialMultiCacheContext = typing.Mapping[
    db_types.SchemaName,
    PartialSingleCacheContext,
]


class SingleCacheContextShorthand(TypedDict, total=False):
    cache: bool | CacheId
    read_cache: bool
    write_cache: bool

