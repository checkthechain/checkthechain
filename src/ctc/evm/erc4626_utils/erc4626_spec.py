from __future__ import annotations

import typing

from ctc import spec


erc4626_event_abis: typing.Mapping[str, spec.EventABI] = {
    'Deposit': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'caller',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'name': 'Deposit',
        'type': 'event',
    },
    'Withdraw': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'caller',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'receiver',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'name': 'Withdraw',
        'type': 'event',
    },
}


# 18 function abis
# - 4 are write functions (deposit, mint, redeem, withdraw)
# - 1 function is metadata (assets)
# - 2 functions are derived from erc20 (balanceOf, totalSupply)
# - 11 functions otherwise
erc4626_function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'asset': {
        'inputs': [],
        'name': 'asset',
        'outputs': [
            {
                'internalType': 'contract ERC20',
                'name': '',
                'type': 'address',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'balanceOf': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'balanceOf',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'convertToAssets': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'name': 'convertToAssets',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'convertToShares': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
        ],
        'name': 'convertToShares',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'deposit': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'receiver',
                'type': 'address',
            },
        ],
        'name': 'deposit',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'maxDeposit': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'recipient',
                'type': 'address',
            },
        ],
        'name': 'maxDeposit',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'maxMint': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'recipient',
                'type': 'address',
            },
        ],
        'name': 'maxMint',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'maxRedeem': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'maxRedeem',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'maxWithdraw': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'maxWithdraw',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'mint': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'receiver',
                'type': 'address',
            },
        ],
        'name': 'mint',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'previewDeposit': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
        ],
        'name': 'previewDeposit',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'previewMint': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'name': 'previewMint',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'previewRedeem': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'name': 'previewRedeem',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'previewWithdraw': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
        ],
        'name': 'previewWithdraw',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'redeem': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'receiver',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'redeem',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'totalAssets': {
        'inputs': [],
        'name': 'totalAssets',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'totalSupply': {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'withdraw': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'assets',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'receiver',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
        ],
        'name': 'withdraw',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': 'shares',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
}
