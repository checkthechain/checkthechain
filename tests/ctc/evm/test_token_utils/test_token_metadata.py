from ctc import evm


fei_address = '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'


def test_get_token_address():
    assert fei_address.lower() == evm.get_erc20_address('FEI').lower()


def test_fetch_token_decimals():
    assert 18 == evm.get_erc20_decimals(fei_address)


def test_fetch_token_name():
    assert 'Fei USD' == evm.get_erc20_name(fei_address)


def test_fetch_token_symbol():
    assert 'FEI' == evm.get_erc20_symbol(fei_address)

