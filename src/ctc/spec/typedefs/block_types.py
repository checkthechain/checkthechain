from __future__ import annotations

import typing
from typing_extensions import TypedDict, Literal, NotRequired

from . import address_types
from . import binary_types
from . import transaction_types


BlockHash = binary_types.PrefixHexData

BlockNumberName = typing.Union[
    Literal['latest'],
    Literal['earliest'],
    Literal['pending'],
]

# anything that can be converted to an int without node querying
RawBlockNumber = typing.Union[typing.SupportsRound, binary_types.HexData, str]


class RawBlock(TypedDict):
    pass

# an int or block number name
StandardBlockNumber = typing.Union[int, BlockNumberName]

# anything that refers to a block number, raw or standard
BlockNumberReference = typing.Union[RawBlockNumber, StandardBlockNumber]

# any reference to a block
BlockReference = typing.Union[BlockNumberReference, BlockHash]


class BlockRange(TypedDict):
    start_block: StandardBlockNumber
    end_block: StandardBlockNumber
    open_start: bool
    open_end: bool


class BlockSample(TypedDict):
    start_block: StandardBlockNumber
    end_block: StandardBlockNumber
    block_interval: typing.Union[int, None]
    open_start: bool
    open_end: bool


class Block(TypedDict):
    base_fee_per_gas: NotRequired[int | None]
    difficulty: int
    extra_data: binary_types.PrefixHexData
    gas_limit: int
    gas_used: int
    hash: BlockHash
    logs_bloom: binary_types.PrefixHexData
    miner: address_types.Address
    mix_hash: BlockHash
    nonce: binary_types.PrefixHexData
    number: int
    parent_hash: BlockHash
    receipts_root: binary_types.PrefixHexData
    sha3_uncles: binary_types.PrefixHexData
    size: int
    state_root: binary_types.PrefixHexData
    timestamp: int
    total_difficulty: str
    transactions: typing.Union[
        typing.List[transaction_types.TransactionHash],
        typing.List[transaction_types.Transaction],
    ]
    transactions_root: binary_types.PrefixHexData
    uncles: typing.List[BlockHash]


class RawLog(TypedDict):
    removed: bool
    logIndex: int
    transactionIndex: int
    transactionHash: transaction_types.TransactionHash
    blockHash: BlockHash
    blockNumber: int
    address: address_types.Address
    data: binary_types.PrefixHexData
    topics: typing.List[binary_types.PrefixHexData]


class PendingRawLog(TypedDict):
    # many log fields are nullable if a log is pending
    removed: bool
    logIndex: typing.Union[None, int]
    transactionIndex: typing.Union[None, int]
    transactionHash: typing.Union[None, transaction_types.TransactionHash]
    blockHash: typing.Union[None, BlockHash]
    blockNumber: typing.Union[None, int]
    address: address_types.Address
    data: binary_types.PrefixHexData
    topics: typing.List[binary_types.PrefixHexData]


NormalizedLog = typing.Dict[str, typing.Any]
