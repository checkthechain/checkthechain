import pytest

from ctc import evm


DAI_CONTRACT = "0x6B175474E89094C44Da98b954EedeAC495271d0F".lower()
START_BLOCK = 15181140
END_BLOCK = 15181147


@pytest.mark.asyncio
async def test_transfer_events():
    df = await evm.async_get_erc20_transfers(
        token=DAI_CONTRACT,
        start_block=START_BLOCK,
        end_block=END_BLOCK,
    )
    assert len(df) == 6
    assert df["contract_address"][0] == DAI_CONTRACT
    assert df["block_number"][0] == START_BLOCK
    assert "timestamp" not in df.columns
