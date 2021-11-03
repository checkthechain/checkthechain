import time

from ctc.evm import rpc_utils


def test_eth_new_filter():
    new_filter = rpc_utils.eth_new_filter()
    assert len(new_filter) > 0 and new_filter.startswith('0x')


def test_eth_new_block_filter():
    new_filter = rpc_utils.eth_new_block_filter()
    assert len(new_filter) > 0 and new_filter.startswith('0x')
    # blocks = rpc_utils.eth_get_filter_changes(new_filter)


def test_eth_new_pending_transaction_filter():
    new_filter = rpc_utils.eth_new_pending_transaction_filter()
    assert len(new_filter) > 0 and new_filter.startswith('0x')
    # pending_transactions = rpc_utils.eth_get_filter_changes(new_filter)


def test_eth_uninstall_filter():
    new_filter = rpc_utils.eth_new_filter()
    rpc_utils.eth_uninstall_filter(new_filter)


def test_eth_get_filter_changes():
    new_filter = rpc_utils.eth_new_pending_transaction_filter()
    time.sleep(3)
    pending_transactions = rpc_utils.eth_get_filter_changes(new_filter)
    assert(len(pending_transactions) > 0)


def test_eth_get_filter_logs():
    new_filter = rpc_utils.eth_new_filter(
        topics=None,
        start_block=None,
        end_block=None,
    )
    new_filter = rpc_utils.eth_new_filter(
        topics=['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'],
        start_block=12345677,
        end_block=12345679,
    )
    logs = rpc_utils.eth_get_filter_logs(new_filter)
    assert len(logs) == 375


def test_eth_get_logs():
    logs = rpc_utils.eth_get_logs(
        topics=['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'],
        start_block=12345677,
        end_block=12345679,
    )
    assert len(logs) == 375

