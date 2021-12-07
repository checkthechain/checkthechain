import typing

from . import token


PrefixHexData = str
RawHexData = str
HexData = typing.Union[PrefixHexData, RawHexData]

BlockHash = PrefixHexData
TransactionHash = PrefixHexData

block_number_names = ['latest', 'earliest', 'pending']
BlockNumberName = typing.Union[
    typing.Literal['latest'],
    typing.Literal['earliest'],
    typing.Literal['pending'],
]

# anything that can be converted to an int without node querying
RawBlockNumber = typing.Union[typing.SupportsInt, HexData]

# an int or block number name
StandardBlockNumber = typing.Union[int, BlockNumberName]

# anything that refers to a block number, raw or standard
BlockNumberReference = typing.Union[RawBlockNumber, StandardBlockNumber]

# any reference to a block
BlockReference = typing.Union[BlockNumberReference, BlockHash]


class RawTransaction(typing.TypedDict):
    pass


class Transaction(typing.TypedDict):
    hash: TransactionHash
    block_hash: BlockHash
    block_number: int
    chain_id: PrefixHexData
    # from: token.Address
    gas: int
    gas_price: int
    input: PrefixHexData
    nonce: int
    r: PrefixHexData
    s: PrefixHexData
    to: token.Address
    transaction_index: int
    type: PrefixHexData
    v: int
    value: int


class RawBlock(typing.TypedDict):
    pass


class Block(typing.TypedDict):
    number: int
    difficulty: int
    extra_data: PrefixHexData
    gas_limit: int
    gas_used: int
    hash: BlockHash
    logs_bloom: PrefixHexData
    miner: token.Address
    mix_hash: BlockHash
    nonce: PrefixHexData
    parent_hash: BlockHash
    receipts_root: PrefixHexData
    sha3_uncles: PrefixHexData
    size: int
    state_root: PrefixHexData
    timestamp: int
    total_difficulty: int
    transactions: typing.Union[list[TransactionHash], list[Transaction]]
    transactions_root: PrefixHexData
    uncles: list[BlockHash]

