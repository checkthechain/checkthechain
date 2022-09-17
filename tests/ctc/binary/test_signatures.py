import pytest

from ctc import evm


def test_pack_vrs_transaction():
    # from https://ethereum.stackexchange.com/a/107498
    target_signature = '0x28a0da4429a9e8e6b54cb101b2df002039f2879ab4ca0e8fae64134942cb81f3e581a03b90a37dc078a82dfc418695b1d4473661aa4d24dd874ac68678894ff44a6b27'
    actual_signature = evm.pack_signature_vrs(
        v='0x28',
        r='0xda4429a9e8e6b54cb101b2df002039f2879ab4ca0e8fae64134942cb81f3e581',
        s='0x3b90a37dc078a82dfc418695b1d4473661aa4d24dd874ac68678894ff44a6b27',
        mode='transaction',
    )
    assert target_signature == actual_signature


private_key_to_public_key_examples = [
    [
        '0x080a12470a639f95139e5e2d9fc7ca597869a42de9bfab4969a3a57a89b0c84a',
        (
            28861520271981833226067272609620060740909575585894736662694419241176299067921,
            104228060715000826995481435060948770188121251882107489647159844236681839901412,
        ),
    ],
    [
        # from https://github.com/ethereum/py_ecc/blob/033b4ea69a3cbc841c02c9b7d1b4996cd7863585/tests/test_secp256k1.py
        '792eca682b890b31356247f2b04662bff448b6bb19ea1c8ab48da222c894ef9b',
        (
            20033694065814990006010338153307081985267967222430278129327181081381512401190,
            72089573118161052907088366229362685603474623289048716349537937839432544970413,
        ),
    ],
]


@pytest.mark.parametrize('test', private_key_to_public_key_examples)
def test_private_key_to_public_key(test):
    private_key, target_public_key = test
    actual_public_key = evm.private_key_to_public_key(private_key)
    assert (
        evm.public_key_tuple_to_hex(target_public_key) == actual_public_key
    )


private_key_to_address_examples = [
    [
        '0x080a12470a639f95139e5e2d9fc7ca597869a42de9bfab4969a3a57a89b0c84a',
        '0x774246187e1e2205c5920898eede0945016080df',
    ],
    [
        b"\xb2\\}\xb3\x1f\xee\xd9\x12''\xbf\t9\xdcv\x9a\x96VK-\xe4\xc4rm\x03[6\xec\xf1\xe5\xb3d",
        '0x5ce9454909639d2d17a3f753ce7d93fa0b9ab12e',
    ],
]


@pytest.mark.parametrize('test', private_key_to_address_examples)
def test_private_key_to_address(test):
    private_key, target_address = test
    actual_address = evm.private_key_to_address(private_key)
    assert target_address == actual_address


sign_text_message_examples = [
    {
        # from https://github.com/ethereum/web3.py/blob/master/docs/web3.eth.account.rst#sign-a-message
        'message': "I♥SF",
        'private_key': b"\xb2\\}\xb3\x1f\xee\xd9\x12''\xbf\t9\xdcv\x9a\x96VK-\xe4\xc4rm\x03[6\xec\xf1\xe5\xb3d",
        'target_signature': (
            28,
            104389933075820307925104709181714897380569894203213074526835978196648170704563,
            28205917190874851400050446352651915501321657673772411533993420917949420456142,
        ),
        'mode': 'personal_sign',
    },
]


@pytest.mark.parametrize('test', sign_text_message_examples)
def test_sign_text_message(test):
    message = test['message']
    private_key = test['private_key']
    target_signature = test['target_signature']
    mode = test['mode']

    actual_signature = evm.sign_text_message(
        message=message,
        private_key=private_key,
        mode=mode,
    )
    assert target_signature == actual_signature


sign_message_hash_examples = [
    {
        # from EIP-155 https://eips.ethereum.org/EIPS/eip-155
        'message_hash': '0xdaf5a779ae972f972197303d7b574746c7ef83eadac0f2791ad23db92e4c8e53',
        'private_key': '0x4646464646464646464646464646464646464646464646464646464646464646',
        'target_signature': (
            37,
            18515461264373351373200002665853028612451056578545711640558177340181847433846,
            46948507304638947509940763649030358759909902576025900602547168820602576006531,
        ),
    },
]


@pytest.mark.parametrize('test', sign_message_hash_examples)
def test_sign_message_hash(test):
    message_hash = test['message_hash']
    private_key = test['private_key']
    target_signature = test['target_signature']

    actual_signature = evm.sign_message_hash(
        message_hash=message_hash,
        private_key=private_key,
        chain_id=1,
    )

    assert target_signature == actual_signature


@pytest.mark.parametrize('test', sign_message_hash_examples)
def test_recover_address(test):
    test = sign_message_hash_examples[0]

    signature = evm.sign_message_hash(
        message_hash=test['message_hash'],
        private_key=test['private_key'],
        chain_id=1,
    )

    target_public_key = evm.private_key_to_public_key(test['private_key'])
    actual_public_key = evm.recover_signer_public_key(
        message_hash=test['message_hash'],
        signature=signature,
    )
    assert actual_public_key == target_public_key

    assert evm.verify_signature(
        signature=signature,
        message_hash=test['message_hash'],
        public_key=target_public_key,
    )
