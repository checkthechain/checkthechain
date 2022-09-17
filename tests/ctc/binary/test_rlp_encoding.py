import pytest
from ctc import evm

rlp_examples = [
    #
    # integers
    [0, '0x80'],
    [15, '0x0f'],
    [1024, '0x820400'],
    #
    # str
    [
        'dog',
        evm.binary_convert(bytes.fromhex('83') + 'dog'.encode(), 'prefix_hex'),
    ],
    [
        ['cat', 'dog'],
        evm.binary_convert(
            bytes.fromhex('c883')
            + 'cat'.encode()
            + bytes.fromhex('83')
            + 'dog'.encode(),
            'prefix_hex',
        ),
    ],
    #
    # lists
    [[], '0xc0'],
    [
        [[], [[]], [[], [[]]]],
        '0xc7c0c1c0c3c0c1c0',
    ],
]


@pytest.mark.parametrize('test', rlp_examples)
def test_rlp_encoding(test):
    data, target_encoding = test
    actual_encoding = evm.rlp_encode(data, str_mode='text')
    assert actual_encoding == target_encoding


#
# # test decoding
#

ascii_examples = [
    'cat',
    'dog',
    'a',
    'hello',
    'world',
    ['hello', 'world'],
    ['nested', ['list', ['structure']]],
    [],
    [[], [[], []]],
]

raw_hex_examples = [
    '636174',
    ['636174'],
    [],
    [[], [[], []]],
]

prefix_hex_examples = [
    '0x636174',
    ['0x636174'],
    [],
    [[], [[], []]],
]


@pytest.mark.parametrize('test', ascii_examples)
def test_rlp_decoding_ascii(test):
    encoded = evm.rlp_encode(test)
    decoded = evm.rlp_decode(encoded, types='ascii')
    assert decoded == test


@pytest.mark.parametrize('test', raw_hex_examples)
def test_rlp_decoding_raw_hex(test):
    encoded = evm.rlp_encode(test, str_mode='hex')
    decoded = evm.rlp_decode(encoded, types='raw_hex')
    assert decoded == test


@pytest.mark.parametrize('test', prefix_hex_examples)
def test_rlp_decoding_prefix_hex(test):
    encoded = evm.rlp_encode(test)
    decoded = evm.rlp_decode(encoded, types='prefix_hex')
    assert decoded == test


#
# # address nonce tuples
#

nonces = [
    0,
    1,
    2,
    3,
    4,
    126,
    127,
    128,
    129,
    256,
    512,
    1024,
    2048,
    65000,
    66000,
    1320000000,
    13200000000000,
]


encoded_ints = [
    '0x80',
    '0x01',
    '0x02',
    '0x03',
    '0x04',
    '0x7e',
    '0x7f',
    '0x8180',
    '0x8181',
    '0x820100',
    '0x820200',
    '0x820400',
    '0x820800',
    '0x82fde8',
    '0x830101d0',
    '0x844ead9a00',
    '0x860c015d4fa000',
]


address = '0x956f47f50a910163d8bf957cf5846d573e7f87ca'
encoded_address = '0x94956f47f50a910163d8bf957cf5846d573e7f87ca'


encoded_address_nonce_tuples = [
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca80',
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca01',
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca02',
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca03',
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca04',
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca7e',
    '0xd694956f47f50a910163d8bf957cf5846d573e7f87ca7f',
    '0xd794956f47f50a910163d8bf957cf5846d573e7f87ca8180',
    '0xd794956f47f50a910163d8bf957cf5846d573e7f87ca8181',
    '0xd894956f47f50a910163d8bf957cf5846d573e7f87ca820100',
    '0xd894956f47f50a910163d8bf957cf5846d573e7f87ca820200',
    '0xd894956f47f50a910163d8bf957cf5846d573e7f87ca820400',
    '0xd894956f47f50a910163d8bf957cf5846d573e7f87ca820800',
    '0xd894956f47f50a910163d8bf957cf5846d573e7f87ca82fde8',
    '0xd994956f47f50a910163d8bf957cf5846d573e7f87ca830101d0',
    '0xda94956f47f50a910163d8bf957cf5846d573e7f87ca844ead9a00',
    '0xdc94956f47f50a910163d8bf957cf5846d573e7f87ca860c015d4fa000',
]


@pytest.mark.parametrize('test', zip(nonces, encoded_ints))
def test_rlp_encode_integer(test):
    integer, target_encoding = test
    assert evm.rlp_encode(integer) == target_encoding


def test_rlp_encode_address():
    assert evm.rlp_encode(address, str_mode='hex') == encoded_address


@pytest.mark.parametrize('test', zip(nonces, encoded_address_nonce_tuples))
def test_rlp_encode_address_integer_tuples(test):
    nonce, target_encoding = test

    assert evm.rlp_encode([address, nonce], str_mode='hex') == target_encoding
