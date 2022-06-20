from __future__ import annotations

import typing

from typing_extensions import TypedDict


ChainId = int
NetworkName = str
NetworkReference = typing.Union[ChainId, NetworkName]


class NetworkMetadata(TypedDict):
    name: NetworkName | None
    chain_id: int
    block_explorer: str | None  # url
