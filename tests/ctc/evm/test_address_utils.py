import pytest

from ctc import evm


yes_is_address_str = [
    '0x0466a390e00c681beb5b1ec398cfd4497b1d223b',
    '0x0466A390E00c681bEB5B1Ec398CFD4497B1d223b',
    '0x0466A390E00C681BEB5B1EC398CFD4497B1D223B',
]

no_is_not_address_str = [
    None,
    0X0466A390E00C681BEB5B1EC398CFD4497B1D223B,
    '0X0466A390E00C681BEB5B1EC398CFD4497B1D223',
    '0466A390E00C681BEB5B1EC398CFD4497B1D223B',
    '0xdee3ac27126b6330c6e08e894077bd8a387a8981f4c1ab41e229528bcd27eacf',
]


@pytest.mark.parametrize('candidate', yes_is_address_str)
def test_is_address_str_true(candidate):
    assert evm.is_address_str(candidate)


@pytest.mark.parametrize('candidate', no_is_not_address_str)
def test_is_address_str_false(candidate):
    assert not evm.is_address_str(candidate)


def test_get_address_checksum():
    assert evm.get_address_checksum('0x0466a390e00c681beb5b1ec398cfd4497b1d223b') == '0x0466A390E00c681bEB5B1Ec398CFD4497B1d223b'


def test_create_reverse_address_map():
    address_map = {
        'Test_1': '0x0466a390e00c681beb5b1ec398cfd4497b1d223b',
        'Test_2': '0x0466a390e00c681beb5b1ec398cfd4497b1d223c',
    }
    ram = evm.create_reverse_address_map(address_map)
    assert len(ram) == 4
    assert ram['0x0466a390e00c681beb5b1ec398cfd4497b1d223b'] == 'Test_1'
    assert ram['0x0466a390e00c681beb5b1ec398cfd4497b1d223c'] == 'Test_2'
    assert ram['0x0466A390E00c681bEB5B1Ec398CFD4497B1d223b'] == 'Test_1'
    assert ram['0x0466A390e00c681beB5b1Ec398cfd4497B1d223C'] == 'Test_2'

