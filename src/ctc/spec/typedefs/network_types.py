from __future__ import annotations

import typing

from typing_extensions import TypedDict


NetworkId = int
NetworkName = str
NetworkReference = typing.Union[NetworkId, NetworkName]


class NetworkMetadata(TypedDict):
    name: NetworkName
    chain_id: int
    block_explorer: str | None  # url
