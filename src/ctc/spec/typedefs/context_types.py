from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import db_types
from . import rpc_types
from . import network_types


class PartialContext(TypedDict, total=False):
    network: network_types.NetworkReference
    provider: rpc_types.ProviderReference
    cache: 'CacheContextShorthand'


class FullContext(TypedDict):
    network: network_types.ChainId
    provider: rpc_types.Provider
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

# name of cache backend, e.g. 'local_sqlite' or 'local_postgres'
CacheBackend = str


class SingleCacheContext(TypedDict):
    backend: CacheBackend
    read: bool
    write: bool


MultiCacheContext = typing.Mapping[
    db_types.SchemaName,
    SingleCacheContext,
]

MutableMultiCacheContext = typing.MutableMapping[
    db_types.SchemaName,
    SingleCacheContext,
]


class PartialSingleCacheContext(TypedDict, total=False):
    backend: CacheBackend
    read: bool
    write: bool


PartialMultiCacheContext = typing.Mapping[
    db_types.SchemaName,
    PartialSingleCacheContext,
]

CacheContextShorthand = typing.Union[
    None,
    bool,
    CacheBackend,
    typing.Mapping[
        db_types.SchemaName,
        typing.Union[bool, CacheBackend, SingleCacheContext],
    ],
]

