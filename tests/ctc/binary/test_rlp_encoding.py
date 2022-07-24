import pytest
from ctc import binary

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
    assert binary.rlp_encode_int(integer) == target_encoding


def test_rlp_encode_address():
    assert binary.rlp_encode_address(address) == encoded_address


@pytest.mark.parametrize('test', zip(nonces, encoded_address_nonce_tuples))
def test_rlp_encode_address_integer_tuples(test):
    nonce, target_encoding = test

    assert binary.rlp_encode_address_nonce_tuple(address, nonce) == target_encoding
