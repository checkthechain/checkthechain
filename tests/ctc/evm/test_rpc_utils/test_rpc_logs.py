import time

import pytest

from ctc import rpc


@pytest.mark.asyncio
async def test_eth_new_filter():
    new_filter = await rpc.async_eth_new_filter()
    assert len(new_filter) > 0 and new_filter.startswith('0x')


@pytest.mark.asyncio
async def test_eth_new_block_filter():
    new_filter = await rpc.async_eth_new_block_filter()
    assert len(new_filter) > 0 and new_filter.startswith('0x')
    # blocks = await rpc.async_eth_get_filter_changes(new_filter)


@pytest.mark.asyncio
async def test_eth_new_pending_transaction_filter():
    new_filter = await rpc.async_eth_new_pending_transaction_filter()
    assert len(new_filter) > 0 and new_filter.startswith('0x')
    # pending_transactions = await rpc.async_eth_get_filter_changes(new_filter)


@pytest.mark.asyncio
async def test_eth_uninstall_filter():
    new_filter = await rpc.async_eth_new_filter()
    await rpc.async_eth_uninstall_filter(new_filter)


@pytest.mark.asyncio
async def test_eth_get_filter_changes():
    new_filter = await rpc.async_eth_new_pending_transaction_filter()
    time.sleep(3)
    pending_transactions = await rpc.async_eth_get_filter_changes(new_filter)
    assert(len(pending_transactions) > 0)


@pytest.mark.asyncio
async def test_eth_get_filter_logs():
    new_filter = await rpc.async_eth_new_filter(
        topics=None,
        start_block=None,
        end_block=None,
    )
    new_filter = await rpc.async_eth_new_filter(
        topics=['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'],
        start_block=12345677,
        end_block=12345679,
    )
    logs = await rpc.async_eth_get_filter_logs(new_filter)
    assert len(logs) == 375


@pytest.mark.asyncio
async def test_eth_get_logs():
    logs = await rpc.async_eth_get_logs(
        topics=['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'],
        start_block=12345677,
        end_block=12345679,
    )
    assert len(logs) == 375

