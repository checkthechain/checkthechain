import pytest

from ctc import evm


fei_address = '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'


async def test_get_token_address():
    assert fei_address.lower() == await evm.async_get_erc20_address('FEI')


@pytest.mark.asyncio
async def test_fetch_token_decimals():
    assert 18 == await evm.async_get_erc20_decimals(fei_address)


@pytest.mark.asyncio
async def test_fetch_token_name():
    assert 'Fei USD' == await evm.async_get_erc20_name(fei_address)


@pytest.mark.asyncio
async def test_fetch_token_symbol():
    assert 'FEI' == await evm.async_get_erc20_symbol(fei_address)
