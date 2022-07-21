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
    df = df.reset_index()
    assert len(df) == 6
    assert df.iloc[0]["contract_address"] == DAI_CONTRACT
    assert df.iloc[0]["block_number"] == START_BLOCK
    assert df.iloc[0]["event_name"] == "Transfer"
    assert "timestamp" not in df.columns
