import pytest

from ctc import evm

# skip tests, hits ratelimit without key

# @pytest.mark.asyncio
# async def test_fetch_eth_total_supply():
#     result = await evm.async_get_eth_total_supply()
#     assert isinstance(result, int)


@pytest.mark.asyncio
async def test_feth_eth_balance():
    result = await evm.async_get_eth_balance(
        address='0x00192Fb10dF37c9FB26829eb2CC623cd1BF599E8',
        block=13437523,
        normalize=False,
    )
    assert result == 3463747527330489047936
