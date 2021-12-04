import pytest

from ctc import evm


yes_is_address_str = [
    '0x0466a390e00c681beb5b1ec398cfd4497b1d223b',
    '0x0466A390E00c681bEB5B1Ec398CFD4497B1d223b',
    '0x0466A390E00C681BEB5B1EC398CFD4497B1D223B',
]

no_is_not_address_str = [
    None,
    0x0466A390E00C681BEB5B1EC398CFD4497B1D223B,
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
    assert (
        evm.get_address_checksum('0x0466a390e00c681beb5b1ec398cfd4497b1d223b')
        == '0x0466A390E00c681bEB5B1Ec398CFD4497B1d223b'
    )


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


# [sender, nonce, result]
create_address_tests = [
    [
        '0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0',
        0,
        '0xcd234a471b72ba2f1ccf0a70fcaba648a5eecd8d',
    ],
    [
        '0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0',
        1,
        '0x343c43a37d37dff08ae8c4a11544c718abb4fcf8',
    ],
    [
        '0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0',
        2,
        '0xf778b86fa74e846c4f0a1fbd1335fe81c00a0c91',
    ],
    [
        '0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0',
        3,
        '0xfffd933a0bc612844eaf0c6fe3e5b8e9b6c1d19c',
    ],
]


@pytest.mark.parametrize('test', create_address_tests)
def test_create_address_create(test):
    sender, nonce, target_result = test
    actual_result = evm.get_created_address(sender=sender, nonce=nonce)
    assert target_result == actual_result


# [sender, salt, init_code, result]
create2_address_tests = [
    [
        '0x0000000000000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000000000000000000000000000',
        '0x00',
        '0x4d1a2e2bb4f88f0250f26ffff098b0b30b26bf38',
    ],
    [
        '0xdeadbeef00000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000000000000000000000000000',
        '0x00',
        '0xb928f69bb1d91cd65274e3c79d8986362984fda3',
    ],
    [
        '0xdeadbeef00000000000000000000000000000000',
        '0x000000000000000000000000feed000000000000000000000000000000000000',
        '0x00',
        '0xd04116cdd17bebe565eb2422f2497e06cc1c9833',
    ],
    [
        '0x0000000000000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000000000000000000000000000',
        '0xdeadbeef',
        '0x70f2b2914a2a4b783faefb75f459a580616fcb5e',
    ],
    [
        '0x00000000000000000000000000000000deadbeef',
        '0x00000000000000000000000000000000000000000000000000000000cafebabe',
        '0xdeadbeef',
        '0x60f3f640a8508fc6a86d45df051962668e1e8ac7',
    ],
    [
        '0x00000000000000000000000000000000deadbeef',
        '0x00000000000000000000000000000000000000000000000000000000cafebabe',
        '0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef',
        '0x1d8bfdc5d46dc4f61d6b6115972536ebe6a8854c',
    ],
    [
        '0x0000000000000000000000000000000000000000',
        '0x0000000000000000000000000000000000000000000000000000000000000000',
        '0x',
        '0xe33c0c7f7df4809055c3eba6c09cfe4baf1bd9e0',
    ],
]


@pytest.mark.parametrize('test', create2_address_tests)
def test_get_reated_address(test):
    sender, salt, init_code, target_result = test
    actual_result = evm.get_created_address(
        sender=sender,
        salt=salt,
        init_code=init_code,
    )
    assert target_result == actual_result

