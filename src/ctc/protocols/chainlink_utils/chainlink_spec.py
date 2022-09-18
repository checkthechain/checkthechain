# https://docs.chain.link/docs/faq/
from __future__ import annotations

import os
import typing
from typing_extensions import TypedDict

from ctc import spec

if typing.TYPE_CHECKING or os.environ.get('BUILDING_SPHINX') == '1':
    _FeedReference = typing.Union[spec.Address, str]

    class FeedRoundData(TypedDict):
        answer: typing.Union[int, float]
        round_id: int
        timestamp: int


path_templates = {
    'feed': '{chainlink_view}/feeds/{feed}/{feed}__{start_block}_to_{end_block}.csv',
}


feed_function_abis: dict[str, spec.FunctionABI] = {
    'aggregator': {
        'inputs': [],
        'name': 'aggregator',
        'outputs': [
            {
                'internalType': 'address',
                'name': '',
                'type': 'address',
            }
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'decimals': {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'description': {
        'inputs': [],
        'name': 'description',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'latestAnswer': {
        'inputs': [],
        'name': 'latestAnswer',
        'outputs': [{'internalType': 'int256', 'name': '', 'type': 'int256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'latestRoundData': {
        'inputs': [],
        'name': 'latestRoundData',
        'outputs': [
            {'internalType': 'uint80', 'name': 'roundId', 'type': 'uint80'},
            {'internalType': 'int256', 'name': 'answer', 'type': 'int256'},
            {'internalType': 'uint256', 'name': 'startedAt', 'type': 'uint256'},
            {'internalType': 'uint256', 'name': 'updatedAt', 'type': 'uint256'},
            {
                'internalType': 'uint80',
                'name': 'answeredInRound',
                'type': 'uint80',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
}

aggregator_event_abis: dict[str, spec.EventABI] = {
    'AnswerUpdated': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'int256',
                'name': 'current',
                'type': 'int256',
            },
            {
                'indexed': True,
                'internalType': 'uint256',
                'name': 'roundId',
                'type': 'uint256',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'updatedAt',
                'type': 'uint256',
            },
        ],
        'name': 'AnswerUpdated',
        'type': 'event',
    },
}
