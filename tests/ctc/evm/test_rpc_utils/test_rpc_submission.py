import pytest

from ctc import rpc


@pytest.mark.asyncio
async def test_eth_gas_price():
    result = await rpc.async_eth_gas_price()
    assert isinstance(result, int)


@pytest.mark.asyncio
async def test_eth_accounts():
    result = await rpc.async_eth_accounts()
    assert isinstance(result, list)
