import pytest

from ctc import evm


@pytest.mark.parametrize(
    'test',
    [
        ['0x1234', 'prefix_hex'],
        ['1234', 'raw_hex'],
        [bytes.fromhex('1234'), 'binary'],
    ],
)
def test_get_binary_format(test):
    data, binary_format = test
    assert evm.get_binary_format(data) == binary_format


@pytest.mark.parametrize(
    'test',
    [
        ['0x1234', 2],
        ['1234', 2],
        [bytes.fromhex('1234'), 2],
    ],
)
def test_get_binary_n_bytes(test):
    data, n_bytes = test
    assert evm.get_binary_n_bytes(data) == n_bytes


conversion_tests = [
    ['1234', 'raw_hex', {}, '1234'],
    ['1234', 'prefix_hex', {}, '0x1234'],
    ['1234', 'binary', {}, bytes.fromhex('1234')],
    ['0x1234', 'raw_hex', {}, '1234'],
    ['0x1234', 'prefix_hex', {}, '0x1234'],
    ['0x1234', 'binary', {}, bytes.fromhex('1234')],
    [bytes.fromhex('1234'), 'raw_hex', {}, '1234'],
    [bytes.fromhex('1234'), 'prefix_hex', {}, '0x1234'],
    [bytes.fromhex('1234'), 'binary', {}, bytes.fromhex('1234')],
]


@pytest.mark.parametrize('test', conversion_tests)
def test_convert(test):
    data, output_format, kwargs, target = test
    assert evm.binary_convert(data, output_format, **kwargs) == target
