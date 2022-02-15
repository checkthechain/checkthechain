import typing
from typing_extensions import TypedDict, Literal

from . import address_types
from . import binary_types


BlockHash = binary_types.PrefixHexData
TransactionHash = binary_types.PrefixHexData

block_number_names = ['latest', 'earliest', 'pending']
BlockNumberName = typing.Union[
    Literal['latest'],
    Literal['earliest'],
    Literal['pending'],
]

# anything that can be converted to an int without node querying
RawBlockNumber = typing.Union[typing.SupportsRound, binary_types.HexData]

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


class RawTransaction(TypedDict):
    pass


# use literal definition because 'from' is a python keyword
Transaction = TypedDict(
    'Transaction',
    {
        'hash': TransactionHash,
        'block_hash': BlockHash,
        'block_number': int,
        'chain_id': binary_types.PrefixHexData,
        'from': address_types.Address,
        'gas': int,
        'gas_price': int,
        'input': binary_types.PrefixHexData,
        'nonce': int,
        'r': binary_types.PrefixHexData,
        's': binary_types.PrefixHexData,
        'to': address_types.Address,
        'transaction_index': int,
        'type': binary_types.PrefixHexData,
        'v': int,
        'value': int,
    },
)


class RawBlock(TypedDict):
    pass


class Block(TypedDict):
    number: int
    difficulty: int
    extra_data: binary_types.PrefixHexData
    gas_limit: int
    gas_used: int
    hash: BlockHash
    logs_bloom: binary_types.PrefixHexData
    miner: address_types.Address
    mix_hash: BlockHash
    nonce: binary_types.PrefixHexData
    parent_hash: BlockHash
    receipts_root: binary_types.PrefixHexData
    sha3_uncles: binary_types.PrefixHexData
    size: int
    state_root: binary_types.PrefixHexData
    timestamp: int
    total_difficulty: int
    transactions: typing.Union[
        typing.List[TransactionHash], typing.List[Transaction]
    ]
    transactions_root: binary_types.PrefixHexData
    uncles: typing.List[BlockHash]


class RawLog(TypedDict):
    removed: bool
    logIndex: int
    transactionIndex: int
    transactionHash: TransactionHash
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
    transactionHash: typing.Union[None, TransactionHash]
    blockHash: typing.Union[None, BlockHash]
    blockNumber: typing.Union[None, int]
    address: address_types.Address
    data: binary_types.PrefixHexData
    topics: typing.List[binary_types.PrefixHexData]


NormalizedLog = typing.Dict[str, typing.Any]

