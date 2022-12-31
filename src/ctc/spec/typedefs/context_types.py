from __future__ import annotations

import typing
from typing_extensions import TypedDict

from . import db_types
from . import rpc_types
from . import network_types


# Context can be any of the context types, either short-hand or full
Context = typing.Union[None, int, str, 'ShorthandContext', 'NormalizedContext']


# ShorthandContext is maximally flexible, allowing many nested data types
class ShorthandContext(TypedDict, total=False):
    network: network_types.NetworkReference | None
    provider: rpc_types.ProviderReference | None
    cache: ContextCacheShorthand


# NormalizedContext is a normalized context dict with all fields present
class NormalizedContext(TypedDict):
    network: network_types.NetworkReference | None
    provider: rpc_types.ProviderReference | None
    cache: typing.Sequence[ContextCacheRule]


# ContextCacheRule specifies cache rules for contexts that satisfy filter
class ContextCacheRule(TypedDict, total=False):
    backend: str
    read: bool
    write: bool
    filter: 'ContextCacheFilter'


# ContextCacheFilter determines the scope of when rule is applicable
class ContextCacheFilter(TypedDict, total=False):
    chain_id: network_types.ChainId | None
    schema: db_types.SchemaName
    backend: str


# ContextCacheShorthand is a maximally flexible cache specification
ContextCacheShorthand = typing.Union[
    None,
    bool,
    str,
    'ContextCacheRule',
    typing.Mapping[
        typing.Union[str, int],
        typing.Union[None, bool, str, 'ContextCacheRule'],
    ],
    typing.Sequence['ContextCacheRule'],
]

