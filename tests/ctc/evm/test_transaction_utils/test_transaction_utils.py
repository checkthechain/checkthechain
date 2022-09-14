import pytest

from ctc import evm


example_txs = [
    '0xccb0a942a36db42ccc5ee226e4f0599c761d4c0a884f3ac2f7a56fef7aef85df',
    '0xfd74b4443e147687326e76886417a5a81c07ba26568c87e928546ef5b8dacd0d',
    '0x0bf99b11e4f4963d34b5b9d24a542ff045d8e436740dcda698ec29deff84c959',
]


@pytest.mark.parametrize('test', example_txs)
async def test_get_tx_hash(test):

    target_hash = test
    transaction = await evm.async_get_transaction(target_hash)
    actual_hash = evm.hash_signed_transaction(transaction)
    assert actual_hash == target_hash


@pytest.mark.parametrize('test', example_txs)
async def test_verify_transaction_signature(test):

    tx_hash = test
    transaction = await evm.async_get_transaction(tx_hash)
    signature = (
        transaction['v'],
        transaction['r'],
        transaction['s'],
    )
    assert evm.verify_transaction_signature(
        signature=signature,
        transaction=transaction,
        address=transaction['from'],
    )


example_transactions = [
    {
        # from https://github.com/ethereum/web3.py/blob/master/docs/web3.eth.account.rst#sign-a-transaction
        'private_key': '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
        'signature': (
            38,
            84095564551732371065849105252408326384410939276686534847013731510862163857293,
            32698347985257114675470251181312399332782188326270244072370350491677872459742,
        ),
        'transaction': {
            'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
            'value': 1000000000,
            'gas': 2000000,
            'max_fee_per_gas': 2000000000,
            'max_priority_fee_per_gas': 1000000000,
            'nonce': 0,
            'chain_id': 1,
            'type': 2,
            'access_list': (
                [
                    '0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
                    [
                        '0x0000000000000000000000000000000000000000000000000000000000000003',
                        '0x0000000000000000000000000000000000000000000000000000000000000007',
                    ],
                ],
                [
                    '0xbb9bc244d798123fde783fcc1c72d3bb8c189413',
                    [],
                ],
            ),
            'input': bytes(),
        },
    },
    {
        # from https://github.com/ethereum/web3.py/blob/master/docs/web3.eth.account.rst#sign-a-transaction
        'private_key': b"\xb2\\}\xb3\x1f\xee\xd9\x12''\xbf\t9\xdcv\x9a\x96VK-\xe4\xc4rm\x03[6\xec\xf1\xe5\xb3d",
        'signature': (
            38,
            93522894155654168208483453926995743737629589441154283159505514235904280342434,
            48417310681110102814014302147799665717176259465062324746227758019974374282313,
        ),
        'transaction': {
            'value': 0,
            'chainId': 1,
            'gas': 70000,
            'maxFeePerGas': 2000000000,
            'maxPriorityFeePerGas': 1000000000,
            'nonce': 0,
            'to': '0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359',
            'data': '0xa9059cbb000000000000000000000000fb6916095ca1df60bb79ce92ce3ea74c37c5d3590000000000000000000000000000000000000000000000000000000000000001',
        },
    },
]


@pytest.mark.parametrize('test', example_transactions)
def test_sign_transaction(test):

    private_key = test['private_key']
    transaction = test['transaction']
    target_signature = test['signature']

    transaction = evm.standardize_transaction(transaction)

    actual_signature = evm.sign_transaction(
        transaction=transaction,
        private_key=private_key,
    )

    assert actual_signature == target_signature
