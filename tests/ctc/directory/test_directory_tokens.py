import pytest
import toolconfig

from ctc import spec
from ctc import directory_new as directory


@pytest.mark.parametrize(
    'query',
    [
        {'symbol': 'USDC'},
        {'address': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'},
        {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'},
    ],
)
def test_get_token_metadata(query):
    metadata = directory.get_token_metadata(network='mainnet', **query)
    toolconfig.conforms_to_spec(metadata, spec.TokenMetadata)


@pytest.mark.parametrize(
    'test',
    [
        ['USDC', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'],
    ],
)
def test_get_token_address(test):
    symbol, address = test
    actual_address = directory.get_token_address(symbol=symbol)
    assert address == actual_address


@pytest.mark.parametrize(
    'test',
    [['0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'USDC']],
)
def test_get_token_symbol(test):
    address, symbol = test
    actual_symbol = directory.get_token_symbol(address=address)
    assert symbol == actual_symbol


def test_load_filesystem_tokens_data():
    tokens_data = directory.load_filesystem_tokens_data('mainnet')
    for token_data in tokens_data:
        toolconfig.conforms_to_spec(token_data, spec.TokenMetadata)

