from __future__ import annotations

import typing

from ctc import spec


erc721_collections = {
    # 'crytpokitties': '0x06012c8cf97bead5deae237070f9587f8e7a266d',
    # 'cryptopunks': '0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb',  # not erc721
    'bayc': '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
    'mayc': '0x60e4d786628fea6478f785a6d7e704777c86a7c6',
    'milady': '0x5af0d9827e0c53e4799bb226655a1de152a425a5',
    'ens': '0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85',
    'artbocks': '0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270',
    'azuki': '0xed5af388653567af2f388e6224dc7c4b3241c544',
    'coolcats': '0x1a92f7381b9f03921564a437210bb9396471050c',
    'uniswapv3position': '0xc36442b4a4522e871399cd717abdd847ab11fe88',
    'loot': '0xff9c1b15b16263c61d017ee9f65c50e4ae0113d7',
    'nouns': '0x9c8ff314c9bc7f6e59a9d9225fb22946427edc03',
    'pudgypenguins': '0xbd3531da5cf5857e7cfaa92426877b022e612cf8',
}


erc721_function_abis: typing.Mapping[str, spec.FunctionABI] = {
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
    'ownerOf': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'tokenId',
                'type': 'uint256',
            },
        ],
        'name': 'ownerOf',
        'outputs': [
            {
                'internalType': 'address',
                'name': '',
                'type': 'address',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getApproved': {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'tokenId',
                'type': 'uint256',
            },
        ],
        'name': 'getApproved',
        'outputs': [
            {
                'internalType': 'address',
                'name': '',
                'type': 'address',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'isApprovedForAll': {
        'inputs': [
            {
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'operator',
                'type': 'address',
            },
        ],
        'name': 'isApprovedForAll',
        'outputs': [
            {
                'internalType': 'bool',
                'name': '',
                'type': 'bool',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
}

erc721_event_abis: typing.Mapping[str, spec.EventABI] = {
    'Approval': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'approved',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'uint256',
                'name': 'tokenId',
                'type': 'uint256',
            },
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
                'indexed': True,
                'internalType': 'uint256',
                'name': 'tokenId',
                'type': 'uint256',
            },
        ],
        'name': 'Transfer',
        'type': 'event',
    },
    'ApprovalForAll': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'owner',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'operator',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'bool',
                'name': 'approved',
                'type': 'bool',
            },
        ],
        'name': 'ApprovalForAll',
        'type': 'event',
    },
}
