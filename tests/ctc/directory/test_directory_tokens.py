import pytest

from ctc import evm


@pytest.mark.parametrize(
    'test',
    [
        ['USDC', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'],
    ],
)
async def test_get_erc20_address(test):
    symbol, address = test
    actual_address = await evm.async_get_erc20_address(symbol)
    assert address == actual_address


@pytest.mark.parametrize(
    'test',
    [['0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'USDC']],
)
async def test_get_erc20_symbol(test):
    address, symbol = test
    actual_symbol = await evm.async_get_erc20_symbol(address)
    assert symbol == actual_symbol
