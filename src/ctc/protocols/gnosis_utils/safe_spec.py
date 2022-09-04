from __future__ import annotations

import typing
from ctc import spec
from typing_extensions import TypedDict


class SafeTransaction(TypedDict):
    to: spec.Address
    value: int
    data: bytes
    operation: int
    safeTxGas: int
    baseGas: int
    gasPrice: int
    gasToken: spec.Address
    refundReceiver: spec.Address
    nonce: int


safe_transaction_keys = [
    'to',
    'value',
    'data',
    'operation',
    'safeTxGas',
    'baseGas',
    'gasPrice',
    'gasToken',
    'refundReceiver',
    'nonce',
]

safe_transaction_type: spec.Eip712StructType = {
    'name': 'SafeTx',
    'fields': {
        'to': 'address',
        'value': 'uint256',
        'data': 'bytes',
        'operation': 'uint8',
        'safeTxGas': 'uint256',
        'baseGas': 'uint256',
        'gasPrice': 'uint256',
        'gasToken': 'address',
        'refundReceiver': 'address',
        'nonce': 'uint256',
    },
}

safe_message_type = {
    'name': 'SafeMessage',
    'fields': {
        'message': 'bytes',
    },
}

function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'getOwners': {
        'inputs': [],
        'name': 'getOwners',
        'outputs': [
            {'internalType': 'address[]', 'name': '', 'type': 'address[]'}
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getThreshold': {
        'inputs': [],
        'name': 'getThreshold',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'nonce': {
        'inputs': [],
        'name': 'nonce',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'execTransaction': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'value',
                'type': 'uint256',
            },
            {
                'internalType': 'bytes',
                'name': 'data',
                'type': 'bytes',
            },
            {
                'internalType': 'enum Enum.Operation',
                'name': 'operation',
                'type': 'uint8',
            },
            {
                'internalType': 'uint256',
                'name': 'safeTxGas',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'baseGas',
                'type': 'uint256',
            },
            {
                'internalType': 'uint256',
                'name': 'gasPrice',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'gasToken',
                'type': 'address',
            },
            {
                'internalType': 'address payable',
                'name': 'refundReceiver',
                'type': 'address',
            },
            {
                'internalType': 'bytes',
                'name': 'signatures',
                'type': 'bytes',
            },
        ],
        'name': 'execTransaction',
        'outputs': [
            {
                'internalType': 'bool',
                'name': 'success',
                'type': 'bool',
            },
        ],
        'stateMutability': 'payable',
        'type': 'function',
    },
}

event_abis = {
    'AddedOwner': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'AddedOwner',
        'type': 'event',
    },
    'ChangedGuard': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'guard',
                'type': 'address',
            },
        ],
        'name': 'ChangedGuard',
        'type': 'event',
    },
    'ChangedThreshold': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'threshold',
                'type': 'uint256',
            },
        ],
        'name': 'ChangedThreshold',
        'type': 'event',
    },
    'ExecutionSuccess': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'bytes32',
                'name': 'txHash',
                'type': 'bytes32',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'payment',
                'type': 'uint256',
            },
        ],
        'name': 'ExecutionSuccess',
        'type': 'event',
    },
    'RemovedOwner': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'RemovedOwner',
        'type': 'event',
    },
    'SafeSetup': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'initiator',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address[]',
                'name': 'owners',
                'type': 'address[]',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'threshold',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'initializer',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'fallbackHandler',
                'type': 'address',
            },
        ],
        'name': 'SafeSetup',
        'type': 'event',
    },
}
