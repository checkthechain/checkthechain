from __future__ import annotations

import typing
from ctc import spec
from typing_extensions import TypedDict, Literal


if typing.TYPE_CHECKING:

    class GnosisSafeCreation(TypedDict):
        creation_block: int
        creation_transaction: spec.PrefixHexData
        factory: spec.Address
        implementation: spec.Address
        address: spec.Address
        version: Literal['1.1', '1.3']

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


safe_deployments_repository = 'https://github.com/safe-global/safe-deployments'

deployments = {
    1: {
        'factory__1.1.1': '0x76e2cfc1f5fa8f6a5b3fc4c8f4788f0116861f9b',
        'factory__1.3.0': '0xa6b71e26c5e0845f74c812102ca7114b6a896ab2',
        'safe__1.0.0': '0xb6029ea3b2c51d09a50b53ca8012feeb05bda35a',
        'safe__1.1.1': '0x34cfac646f301356faa8b21e94227e3583fe3f5f',
        'safe__1.2.0': '0x6851d6fdfafd08c0295c392436245e5bc78b0185',
        'safe__1.3.0': '0xd9db270c1b5e3bd161e8c8503c55ceabee709552',
        'safe_l2__1.3.0': '0x3e5c63644e683549055b9be8653de26e0b4cd36e',
    }
}

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
