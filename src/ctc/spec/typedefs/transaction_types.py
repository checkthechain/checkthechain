from __future__ import annotations

import typing
from typing_extensions import TypedDict, NotRequired

from . import address_types
from . import binary_types


class RawTransaction(TypedDict):
    pass


TransactionHash = binary_types.PrefixHexData

# use literal definition because 'from' is a python keyword
Transaction = TypedDict(
    'Transaction',
    {
        'hash': TransactionHash,
        'block_hash': binary_types.PrefixHexData,
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
    access_list: typing.Sequence[
        typing.Tuple[
            address_types.Address,
            typing.Sequence[binary_types.PrefixHexData],
        ]
    ]
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
    access_list: typing.Sequence[
        typing.Tuple[
            address_types.Address,
            typing.Sequence[binary_types.PrefixHexData],
        ]
    ]
    #
    # included once sigend
    v: NotRequired[binary_types.Data]
    r: NotRequired[binary_types.Data]
    s: NotRequired[binary_types.Data]
    #
    # other data
    type: NotRequired[binary_types.Data]


TransactionData = typing.Union[
    LegacyTransaction,
    EIP2930Transaction,
    EIP1559Transaction,
]
