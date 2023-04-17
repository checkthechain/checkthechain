"""

## Transaction Types
0. legacy
1. [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)
2. [EIP-2930](https://eips.ethereum.org/EIPS/eip-2930)
"""
from __future__ import annotations

import typing

from . import address_types
from . import log_types
from . import binary_types

from typing_extensions import TypedDict, NotRequired


TransactionHash = binary_types.PrefixHexData

TransactionAccessList = typing.Sequence[
    # tuples describe accessed data as (contract, memory_slot)
    typing.Tuple[
        address_types.Address,
        typing.Sequence[binary_types.PrefixHexData],
    ]
]


#
# # pre-chain transaction types
#

# these transaction types are either sign-able or submit-able

class LegacyTransaction(TypedDict):
    #
    # used for pre-sign hash
    nonce: int
    gas_price: int
    gas: int
    to: address_types.Address
    value: int
    input: binary_types.Data
    #
    # included once sigend
    v: NotRequired[binary_types.Data]
    r: NotRequired[binary_types.Data]
    s: NotRequired[binary_types.Data]
    #
    # other data
    chain_id: NotRequired[binary_types.Data]
    type: int


class EIP2930Transaction(TypedDict):
    #
    # used for pre-sign hash
    chain_id: int
    nonce: int
    gas_price: int
    gas: int
    to: address_types.Address
    value: int
    input: binary_types.Data
    access_list: TransactionAccessList
    #
    # included once sigend
    v: NotRequired[binary_types.Data]
    r: NotRequired[binary_types.Data]
    s: NotRequired[binary_types.Data]
    #
    # other data
    type: NotRequired[binary_types.Data]


class EIP1559Transaction(TypedDict):
    #
    # used for pre-sign hash
    chain_id: int
    nonce: int
    max_priority_fee_per_gas: int
    max_fee_per_gas: int
    gas: int
    to: address_types.Address
    value: int
    input: binary_types.Data
    access_list: TransactionAccessList
    #
    # included once sigend
    v: NotRequired[binary_types.Data]
    r: NotRequired[binary_types.Data]
    s: NotRequired[binary_types.Data]
    #
    # other data
    type: NotRequired[binary_types.Data]


PrechainTransaction = typing.Union[
    LegacyTransaction,
    EIP2930Transaction,
    EIP1559Transaction,
]


#
# # RPC transaction types
#

# these transaction types are the results of RPC requests

RPCTransaction = TypedDict(
    'RPCTransaction',
    {
        'access_list': NotRequired[TransactionAccessList],
        'block_hash': binary_types.PrefixHexData,
        'block_number': int,
        'chain_id': binary_types.PrefixHexData,
        'from': address_types.Address,
        'gas': int,
        'gas_price': int,
        'hash': TransactionHash,
        'input': binary_types.PrefixHexData,
        'max_fee_per_gas': NotRequired[int],
        'max_priority_fee_per_gas': NotRequired[int],
        'nonce': int,
        'r': binary_types.PrefixHexData,
        's': binary_types.PrefixHexData,
        'to': address_types.Address,
        'transaction_index': int,
        'type': int,
        'v': int,
        'value': int,
    },
)

RPCTransactionReceipt = TypedDict(
    'RPCTransactionReceipt',
    {
        'block_hash': str,
        'block_number': int,
        'contract_address': str,
        'cumulative_gas_used': int,
        'effective_gas_price': int,
        'from': str,
        'gas_used': int,
        'logs': typing.Sequence[log_types.RawLog],
        'logs_bloom': str,
        'status': int,
        'to': str,
        'transaction_hash': str,
        'transaction_index': int,
        'type': int,
    },
)


#
# # DB transaction types
#

# these transaction types are stored in the ctc DB

class DBTransaction(TypedDict):
    hash: TransactionHash
    block_number: int
    transaction_index: int
    to_address: address_types.Address
    from_address: address_types.Address
    value: int
    input: str
    nonce: int
    transaction_type: int
    status: int
    gas_used: int
    gas_limit: int
    gas_priority: int | None
    gas_price: int
    gas_price_max: int | None
    access_list: TransactionAccessList | None


# convert large fields to str
class DBTransactionText(TypedDict):
    hash: TransactionHash
    block_number: int
    transaction_index: int
    to_address: address_types.Address
    from_address: address_types.Address
    value: str
    input: str
    nonce: int
    transaction_type: int
    status: int
    gas_used: int
    gas_limit: int
    gas_priority: int | None
    gas_price: int
    gas_price_max: int | None
    access_list: TransactionAccessList | None

