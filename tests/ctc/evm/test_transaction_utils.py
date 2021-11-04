from ctc import evm
from ctc import config_utils


transaction_hash = '0xdee3ac27126b6330c6e08e894077bd8a387a8981f4c1ab41e229528bcd27eacf'


def test_get_transactions():
    print(config_utils.get_config())
    transaction = evm.fetch_transaction(transaction_hash)
    assert transaction['block_number'] == 13436349

