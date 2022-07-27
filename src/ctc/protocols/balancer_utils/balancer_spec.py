from __future__ import annotations

import typing

from ctc import spec


vault = '0xba12222222228d8ba445958a75a0704d566bf2c8'


vault_function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'getPool': {
        'inputs': [
            {
                'internalType': 'bytes32',
                'name': 'poolId',
                'type': 'bytes32',
            },
        ],
        'name': 'getPool',
        'outputs': [
            {
                'internalType': 'address',
                'name': '',
                'type': 'address',
            },
            {
                'internalType': 'enum IVault.PoolSpecialization',
                'name': '',
                'type': 'uint8',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getPoolTokens': {
        'inputs': [
            {
                'internalType': 'bytes32',
                'name': 'poolId',
                'type': 'bytes32',
            },
        ],
        'name': 'getPoolTokens',
        'outputs': [
            {
                'internalType': 'contract IERC20[]',
                'name': 'tokens',
                'type': 'address[]',
            },
            {
                'internalType': 'uint256[]',
                'name': 'balances',
                'type': 'uint256[]',
            },
            {
                'internalType': 'uint256',
                'name': 'lastChangeBlock',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
}
