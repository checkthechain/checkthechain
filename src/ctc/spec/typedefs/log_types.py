from __future__ import annotations

import typing
from typing_extensions import TypedDict


class RawLog(TypedDict):
    removed: bool
    logIndex: int
    transactionIndex: int
    transactionHash: str
    blockHash: str
    blockNumber: int
    address: str
    data: str
    topics: typing.List[str]


class PendingRawLog(TypedDict):
    # many log fields are nullable if a log is pending
    removed: bool
    logIndex: typing.Union[None, int]
    transactionIndex: typing.Union[None, int]
    transactionHash: typing.Union[None, str]
    blockHash: typing.Union[None, str]
    blockNumber: typing.Union[None, int]
    address: str
    data: str
    topics: typing.List[str]


NormalizedLog = typing.Dict[str, typing.Any]

