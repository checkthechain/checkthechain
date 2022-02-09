import pytest

from ctc import binary


keccak_data_pairs = [
    [
        '0x689268c0ff57a20cd299fa60d3fb374862aff565b20b5f1767906a99e6e09f3ff04ca2b2a5cd22f62941db103c0356df1a8ed20ce322cab2483db67685afd124',
        '0xde77577a693274e6d5e229c326d1ec50b4e62c1d1a40d16e7cacc6a6580757d5'
    ],
]

keccak_text_pairs = [
    [
        'Transfer(address,address,uint256)',
        '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
    ],
]


@pytest.mark.parametrize('input_output', keccak_data_pairs)
def test_keccak(input_output):
    assert binary.keccak(input_output[0], 'prefix_hex') == input_output[1]


@pytest.mark.parametrize('input_output', keccak_text_pairs)
def test_keccak_text(input_output):
    assert binary.keccak_text(input_output[0], 'prefix_hex') == input_output[1]

