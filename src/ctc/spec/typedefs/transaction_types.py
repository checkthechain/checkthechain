from __future__ import annotations

import typing
from typing_extensions import TypedDict, NotRequired

from . import address_types
from . import log_types
from . import binary_types


TransactionHash = binary_types.PrefixHexData

TransactionAccessList = typing.Sequence[
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
        'block_hash': binary_types.PrefixHexData,
        'block_number': int,
        'from': address_types.Address,
        'gas': int,
        'gas_price': int,
        'hash': TransactionHash,
        'input': binary_types.PrefixHexData,
        'nonce': int,
        'to': address_types.Address,
        'transaction_index': int,
        'value': int,
        'type': binary_types.PrefixHexData,
        'chain_id': binary_types.PrefixHexData,
        'v': int,
        'r': binary_types.PrefixHexData,
        's': binary_types.PrefixHexData,
        #
        # newer attributes that may or may not be present
        'max_priority_fee_per_gas': NotRequired[int],
        'max_fee_per_gas': NotRequired[int],
        'access_list': NotRequired[TransactionAccessList],
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

DBTransaction = TypedDict(
    'DBTransaction',
    {
        'hash': TransactionHash,
        'block_number': int,
        'transaction_index': int,
        'to': address_types.Address,
        'from': address_types.Address,
        'value': int,
        'input': str,
        'nonce': int,
        'type': int,
        'access_list': typing.Sequence[str],
        'gas_used': int,
        'gas_price': int,
    },
)

