
from ctc import evm


def test_fetch_eth_total_supply():
    result = evm.fetch_eth_total_supply()
    assert isinstance(result, int)


def test_feth_eth_balance():
    result = evm.fetch_eth_balance(
        address='0x00192Fb10dF37c9FB26829eb2CC623cd1BF599E8',
        block=13437523,
        normalize=False,
    )
    assert result == 3463747527330489047936
