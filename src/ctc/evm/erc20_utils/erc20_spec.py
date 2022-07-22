from __future__ import annotations

from ctc import spec


erc20_function_abis: dict[str, spec.FunctionABI] = {
    'name': {
        'inputs': [],
        'name': 'name',
        'outputs': [{'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'approve': {
        'inputs': [
            {'name': '_spender', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'},
        ],
        'name': 'approve',
        'outputs': [{'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'totalSupply': {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'transferFrom': {
        'inputs': [
            {'name': '_from', 'type': 'address'},
            {'name': '_to', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'},
        ],
        'name': 'transferFrom',
        'outputs': [{'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'decimals': {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint8'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'balanceOf': {
        'inputs': [{'name': '_owner', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': 'balance', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'symbol': {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'transfer': {
        'inputs': [
            {'name': '_to', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'},
        ],
        'name': 'transfer',
        'outputs': [{'name': '', 'type': 'bool'}],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'allowance': {
        'inputs': [
            {'name': '_owner', 'type': 'address'},
            {'name': '_spender', 'type': 'address'},
        ],
        'name': 'allowance',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
}


erc20_event_abis: dict[str, spec.EventABI] = {
    'Approval': {
        'anonymous': False,
        'inputs': [
            {'indexed': True, 'name': 'owner', 'type': 'address'},
            {'indexed': True, 'name': 'spender', 'type': 'address'},
            {'indexed': False, 'name': 'value', 'type': 'uint256'},
        ],
        'name': 'Approval',
        'type': 'event',
    },
    'Transfer': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'from',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount',
                'type': 'uint256',
            },
        ],
        'name': 'Transfer',
        'type': 'event',
    },
}
