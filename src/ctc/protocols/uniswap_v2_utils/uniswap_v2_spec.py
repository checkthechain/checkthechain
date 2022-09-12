from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


uniswap_v2_factory = '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f'

trade_fee = 0.003


class PoolTokensMetadata(TypedDict):
    x_address: spec.Address
    y_address: spec.Address
    x_symbol: str
    y_symbol: str
    x_decimals: int
    y_decimals: int


class PoolState(TypedDict):
    x_reserves: typing.Union[int, float]
    y_reserves: typing.Union[int, float]
    lp_total_supply: typing.Union[int, float]


class PoolStateByBlock(TypedDict):
    x_reserves: list[typing.Union[int, float]]
    y_reserves: list[typing.Union[int, float]]
    lp_total_supply: list[typing.Union[int, float]]


factory_event_abis: typing.Mapping[str, spec.EventABI] = {
    'PairCreated': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'token0',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'token1',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'address',
                'name': 'pair',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'name': 'PairCreated',
        'type': 'event',
    },
}


pool_function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'token0': {
        'inputs': [],
        'name': 'token0',
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
    'token1': {
        'inputs': [],
        'name': 'token1',
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
}


pool_event_abis: typing.Mapping[str, spec.EventABI] = {
    'Burn': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'sender',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount0',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount1',
                'type': 'uint256',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
        ],
        'name': 'Burn',
        'type': 'event',
    },
    'Mint': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'sender',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount0',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount1',
                'type': 'uint256',
            },
        ],
        'name': 'Mint',
        'type': 'event',
    },
    'Swap': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'sender',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount0In',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount1In',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount0Out',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount1Out',
                'type': 'uint256',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
        ],
        'name': 'Swap',
        'type': 'event',
    },
}
