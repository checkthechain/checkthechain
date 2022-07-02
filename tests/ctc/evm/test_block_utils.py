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


block_timestamps = {
    4019263: 1500000000,
    10853627: 1600000000,
}


@pytest.mark.asyncio
@pytest.mark.parametrize('block_timestamp', block_timestamps.items())
async def test_get_block_of_timestamp(block_timestamp):
    block, timestamp = block_timestamp
    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp, use_db=False, use_db_assist=False
    )
    assert block == obtained_block

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp, use_db=False, use_db_assist=True
    )
    assert block == obtained_block

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp, use_db=True
    )
    assert block == obtained_block


@pytest.mark.asyncio
@pytest.mark.parametrize('block_timestamp', block_timestamps.items())
@pytest.mark.parametrize(
    'db_settings', [[False, False], [False, True], [True, True]]
)
async def test_block_of_timestamp_modes(block_timestamp, db_settings):
    block, _ = block_timestamp
    use_db, use_db_assist = db_settings

    block_data = await evm.async_get_block(block)

    timestamp = block_data['timestamp']
    timestamp_after = timestamp + 1

    # test using exact timestamp

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp, mode='==', use_db=use_db, use_db_assist=use_db_assist
    )
    assert obtained_block == block

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp, mode='<=', use_db=use_db, use_db_assist=use_db_assist
    )
    assert obtained_block == block

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp, mode='>=', use_db=use_db, use_db_assist=use_db_assist
    )
    assert obtained_block == block

    # test using offset timestamp
    with pytest.raises(Exception):
        obtained_block = await evm.async_get_block_of_timestamp(
            timestamp_after,
            mode='==',
            use_db=use_db,
            use_db_assist=use_db_assist,
        )

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp_after, mode='<=', use_db=use_db, use_db_assist=use_db_assist
    )
    assert obtained_block == block

    obtained_block = await evm.async_get_block_of_timestamp(
        timestamp_after, mode='>=', use_db=use_db, use_db_assist=use_db_assist
    )
    assert obtained_block == block + 1
