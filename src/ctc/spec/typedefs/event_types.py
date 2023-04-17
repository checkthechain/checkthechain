from __future__ import annotations

import typing

from typing_extensions import TypedDict, NotRequired

from . import address_types
from . import binary_types


class EncodedEvent(TypedDict):
    block_number: int
    transaction_index: int
    log_index: int
    transaction_hash: str
    contract_address: address_types.Address
    event_hash: str
    topic1: typing.Any
    topic2: typing.Any
    topic3: typing.Any
    unindexed: typing.Any


class EventQuery(TypedDict):
    contract_address: address_types.Address | None
    event_hash: typing.Any | None
    topic1: binary_types.BinaryData | None
    topic2: binary_types.BinaryData | None
    topic3: binary_types.BinaryData | None
    start_block: int
    end_block: int


class DBEventQuery(TypedDict):
    query_id: NotRequired[int]
    query_type: int
    contract_address: address_types.Address | None
    event_hash: typing.Any | None
    topic1: binary_types.BinaryData | None
    topic2: binary_types.BinaryData | None
    topic3: binary_types.BinaryData | None
    start_block: int
    end_block: int


class EventQueryPlan(TypedDict):
    db: typing.Sequence[EventQuery]
    node: typing.Sequence[EventQuery]
