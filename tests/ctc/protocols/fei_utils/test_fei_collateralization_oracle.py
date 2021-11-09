from ctc import directory
from ctc.protocols import fei_utils


def test_get_deposits_for_token():

    deposits = fei_utils.get_deposits_for_token(
        token=directory.token_addresses['DPI'],
        block=13570382,
        wrapper=False,
    )
    assert deposits == (
        '0x60b63ef8f461355207fe1d8102dda938bbd8c3fb',
        '0x9a774a1b1208c323eded05e6daf592e6e59caa55',
        '0x902199755219a9f8209862d09f1891cfb34f59a3',
    )


def test_get_deposit_token_balance():

    balance = fei_utils.get_deposit_token_balance(
        deposit_address='0x60b63ef8f461355207fe1d8102dda938bbd8c3fb',
        block=13570382,
    )

    assert balance == 154408399224631216120


def test_get_tokens_in_pcv():
    tokens = fei_utils.get_tokens_in_pcv(block=13570382, wrapper=False)
    assert tokens == (
        '0x1111111111111111111111111111111111111111',
        '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
        '0x6b175474e89094c44da98b954eedeac495271d0f',
        '0x03ab458634910aad20ef5f1c8ee96f1d6ac54919',
        '0x1494ca1f11d487c2bbe4543e90080aeba4ba3c2b',
        '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
    )


def test_token_to_oracle():
    oracle = fei_utils.token_to_oracle(
        '0x6b175474e89094c44da98b954eedeac495271d0f',
        block=13570382,
    )
    assert oracle == '0x231ada12e273edf3fa54cbd90c5c1a73129d5bb9'

