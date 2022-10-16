from __future__ import annotations

import pytest

import ctc


example_deposits = [
    {
        'kwargs': {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'start_block': 15060729,
            'end_block': 15755513,
        },
        'n_results': 49,
    },
]

example_withdraws = [
    {
        'kwargs': {
            'token': '0xf9a98a9452485ed55cd3ce5260c2b71c9807b11a',
            'start_block': 15060729,
            'end_block': 15755513,
        },
        'n_results': 19,
    },
]


@pytest.mark.parametrize('example', example_deposits)
async def test_get_erc4626_deposits(example):
    deposits = await ctc.async_get_erc4626_deposits(**example['kwargs'])
    assert len(deposits) == example['n_results']


@pytest.mark.parametrize('example', example_withdraws)
async def test_get_erc4626_withdraws(example):
    withdraws = await ctc.async_get_erc4626_withdraws(**example['kwargs'])
    assert len(withdraws) == example['n_results']
