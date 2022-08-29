import pytest

from ctc import binary
from ctc import evm


def test_pack_vrs_transaction():
    # from https://ethereum.stackexchange.com/a/107498
    target_signature = '0x28a0da4429a9e8e6b54cb101b2df002039f2879ab4ca0e8fae64134942cb81f3e581a03b90a37dc078a82dfc418695b1d4473661aa4d24dd874ac68678894ff44a6b27'
    actual_signature = binary.pack_vrs(
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
    actual_public_key = binary.private_key_to_public_key(private_key)
    assert (
        binary.public_key_tuple_to_hex(target_public_key) == actual_public_key
    )


private_key_to_address_examples = [
    [
        '0x080a12470a639f95139e5e2d9fc7ca597869a42de9bfab4969a3a57a89b0c84a',
        '0x774246187e1e2205c5920898eede0945016080df',
    ]
]


@pytest.mark.parametrize('test', private_key_to_address_examples)
def test_private_key_to_address(test):
    private_key, target_address = test
    actual_address = binary.private_key_to_address(private_key)
    assert target_address == actual_address


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

    actual_signature = binary.sign_message_hash(
        message_hash=message_hash,
        private_key=private_key,
        chain_id=1,
    )

    assert target_signature == actual_signature


def test_recover_address():
    test = sign_message_hash_examples[0]

    signature = binary.sign_message_hash(
        message_hash=test['message_hash'],
        private_key=test['private_key'],
        chain_id=1,
    )

    target_public_key = binary.private_key_to_public_key(test['private_key'])
    actual_public_key = binary.get_signer_public_key(
        message_hash=test['message_hash'],
        signature=signature,
    )
    assert actual_public_key == target_public_key


example_txs = [
    '0xccb0a942a36db42ccc5ee226e4f0599c761d4c0a884f3ac2f7a56fef7aef85df',
    '0xfd74b4443e147687326e76886417a5a81c07ba26568c87e928546ef5b8dacd0d',
    '0x0bf99b11e4f4963d34b5b9d24a542ff045d8e436740dcda698ec29deff84c959',
]


@pytest.mark.parametrize('test', example_txs)
async def test_get_tx_hash(test):

    target_hash = test
    transaction = await evm.async_get_transaction(target_hash)
    actual_hash = binary.get_signed_transaction_hash(transaction)
    assert actual_hash == target_hash
