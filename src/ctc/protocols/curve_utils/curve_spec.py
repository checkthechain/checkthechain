"""
see https://github.com/curvefi/curve-pool-registry
"""
from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


three_pool_lp = '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490'
three_pool = '0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7'
three_pool_token_index = {
    'DAI': 0,
    'USDC': 1,
    'USDT': 2,
}
three_pool_coins = ['DAI', 'USDC', 'USDT']


class CurvePoolMetadata(TypedDict):
    token_addresses: list[spec.Address]
    token_symbols: list[str]
    token_decimals: list[int]
    A: int


class CurveTrade(TypedDict):
    token_sold: spec.Address
    token_bought: spec.Address
    amount_sold: typing.Union[int, float]
    amount_bought: typing.Union[int, float]


pool_function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'A': {
        'inputs': [],
        'name': 'A',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'future_A': {
        'inputs': [],
        'name': 'future_A',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'future_A_time': {
        'inputs': [],
        'name': 'future_A_time',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'initial_A': {
        'inputs': [],
        'name': 'initial_A',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'initial_A_time': {
        'inputs': [],
        'name': 'initial_A_time',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'calc_withdraw_one_coin': {
        'inputs': [
            {
                'name': '_burn_amount',
                'type': 'uint256',
            },
            {
                'name': 'i',
                'type': 'int128',
            },
        ],
        'name': 'calc_withdraw_one_coin',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'get_dy': {
        'inputs': [
            {
                'name': 'i',
                'type': 'int128',
            },
            {
                'name': 'j',
                'type': 'int128',
            },
            {
                'name': 'dx',
                'type': 'uint256',
            },
        ],
        'name': 'get_dy',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'get_virtual_price': {
        'inputs': [],
        'name': 'get_virtual_price',
        'outputs': [
            {
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
}

pool_event_abis = {
    'TokenExchange': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'name': 'buyer',
                'type': 'address',
            },
            {
                'indexed': False,
                'name': 'sold_id',
                'type': 'int128',
            },
            {
                'indexed': False,
                'name': 'tokens_sold',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'name': 'bought_id',
                'type': 'int128',
            },
            {
                'indexed': False,
                'name': 'tokens_bought',
                'type': 'uint256',
            },
        ],
        'name': 'TokenExchange',
        'type': 'event',
    },
    'TokenExchangeUnderlying': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'name': 'buyer',
                'type': 'address',
            },
            {
                'indexed': False,
                'name': 'sold_id',
                'type': 'int128',
            },
            {
                'indexed': False,
                'name': 'tokens_sold',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'name': 'bought_id',
                'type': 'int128',
            },
            {
                'indexed': False,
                'name': 'tokens_bought',
                'type': 'uint256',
            },
        ],
        'name': 'TokenExchangeUnderlying',
        'type': 'event',
    },
}
