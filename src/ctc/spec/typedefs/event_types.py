from __future__ import annotations

import typing

from . import address_types

from typing_extensions import TypedDict


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


class EventQuery(TypedDict):
    contract_address: address_types.Address | None
    topics: typing.Sequence[typing.Any] | None
    start_block: int
    end_block: int


class EventQueryRoute(TypedDict):
    db: typing.Sequence[EventQuery]
    node: typing.Sequence[EventQuery]
