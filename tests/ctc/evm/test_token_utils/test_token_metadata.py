from ctc import evm


fei_address = '0x956F47F50A910163D8BF957Cf5846D573E7f87CA'


def test_get_token_address():
    assert fei_address == evm.get_token_address('FEI')


def test_fetch_token_decimals():
    assert 18 == evm.fetch_token_decimals(fei_address)


def test_fetch_token_name():
    assert 'Fei USD' == evm.fetch_token_name(fei_address)


def test_fetch_token_symbol():
    assert 'FEI' == evm.fetch_token_symbol(fei_address)

