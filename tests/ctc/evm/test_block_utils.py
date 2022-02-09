import pytest

from ctc import evm


@pytest.mark.asyncio
async def test_get_block():
    latest_block = await evm.async_get_block('latest')
    assert latest_block is not None


@pytest.mark.asyncio
async def test_fetch_latest_block_number():
    latest_block_number = await evm.async_get_latest_block_number()
    assert isinstance(latest_block_number, int)


@pytest.mark.asyncio
async def test_get_contract_creation_block():
    contract = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
    result = await evm.async_get_contract_creation_block(contract)
    target = 8928158
    assert result == target

