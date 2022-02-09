import pytest

from ctc import directory
from ctc.protocols import fei_utils


@pytest.mark.asyncio
async def test_get_tokens_deposits():

    deposits = await fei_utils.async_get_token_deposits(
        directory.get_erc20_address('DPI'),
        block=13570382,
    )
    assert deposits == (
        '0x60b63ef8f461355207fe1d8102dda938bbd8c3fb',
        '0x9a774a1b1208c323eded05e6daf592e6e59caa55',
        '0x902199755219a9f8209862d09f1891cfb34f59a3',
    )


@pytest.mark.asyncio
async def test_get_deposit_token_balance():

    balance = await fei_utils.async_get_deposit_balance(
        '0x60b63ef8f461355207fe1d8102dda938bbd8c3fb',
        block=13570382,
    )

    assert balance == 154408399224631216120


@pytest.mark.asyncio
async def test_get_tokens_in_pcv():
    tokens = await fei_utils.async_get_tokens_in_pcv(block=13570382, wrapper=False)
    assert tokens == (
        '0x1111111111111111111111111111111111111111',
        '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
        '0x6b175474e89094c44da98b954eedeac495271d0f',
        '0x03ab458634910aad20ef5f1c8ee96f1d6ac54919',
        '0x1494ca1f11d487c2bbe4543e90080aeba4ba3c2b',
        '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    )


@pytest.mark.asyncio
async def test_token_to_oracle():
    oracle = await fei_utils.async_get_token_oracle(
        '0x6b175474e89094c44da98b954eedeac495271d0f',
        block=13570382,
    )
    assert oracle == '0x231ada12e273edf3fa54cbd90c5c1a73129d5bb9'

