from ctc.evm import rpc_utils


def test_eth_gas_price():
    result = rpc_utils.eth_gas_price()
    assert isinstance(result, int)


def test_eth_accounts():
    result = rpc_utils.eth_accounts()
    assert isinstance(result, list)

