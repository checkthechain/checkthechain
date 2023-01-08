from __future__ import annotations

import typing
from typing_extensions import TypedDict, Literal, NotRequired

from . import address_types
from . import binary_types
from . import transaction_types


#
# # block references
#

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


#
# # block data
#

# block returned from RPC request
class RPCBlock(TypedDict):
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
        typing.List[transaction_types.RPCTransaction],
    ]
    transactions_root: binary_types.PrefixHexData
    uncles: typing.List[BlockHash]


class DBBlock(TypedDict):
    number: int
    hash: str
    timestamp: int
    miner: str
    extra_data: str
    base_fee_per_gas: int | None
    gas_limit: int
    gas_used: int

