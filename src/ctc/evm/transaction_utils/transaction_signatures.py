from __future__ import annotations

import typing

from ctc import spec
from .. import binary_utils
from . import transaction_serialize
from . import transaction_hashes
from . import transaction_types


def sign_transaction(
    transaction: spec.TransactionData,
    *,
    private_key: str,
    chain_id: int | None = None,
) -> tuple[int, int, int]:
    """sign transaction using private key"""

    if chain_id is None and 'chain_id' in transaction:
        tx_chain_id = transaction['chain_id']
        if tx_chain_id is not None:
            chain_id = binary_utils.binary_convert(tx_chain_id, 'integer')
    message = transaction_serialize.serialize_unsigned_transaction(
        transaction,
        chain_id=chain_id,
    )
    return binary_utils.sign_data_message(
        message=message,
        private_key=private_key,
        chain_id=chain_id,
        mode='eth_sign',
    )


def verify_transaction_signature(
    *,
    transaction: spec.TransactionData,
    signature: spec.Signature | None = None,
    public_key: spec.Data | None = None,
    address: spec.Data | None = None,
) -> bool:
    """verify that transaction was signed by given public key"""

    # extract signature from transaction
    if signature is None:
        if (
            transaction.get('v') is not None
            and transaction.get('r') is not None
            and transaction.get('s') is not None
        ):
            signature = (transaction['v'], transaction['r'], transaction['s'])
        else:
            raise Exception('must provide signature for transaction')

    # get transaction hash
    transaction_hash = transaction_hashes.hash_unsigned_transaction(transaction)

    # process signature
    v, r, s = binary_utils.unpack_signature_vrs(signature)
    type = transaction_types.get_transaction_type(transaction)
    if type == 2 and v in [0, 1]:
        v = v + 27

    # verify signature
    return binary_utils.verify_signature(
        signature=(v, r, s),
        message_hash=transaction_hash,
        public_key=public_key,
        address=address,
    )


def recover_transaction_sender(
    transaction: spec.TransactionData,
    signature: spec.Signature,
) -> spec.Address:
    """recover signing address of transaction from signature

    adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/transactions.py#L68
    """

    if 'from' in transaction:
        return transaction['from']  # type: ignore

    v, r, s = binary_utils.unpack_signature_vrs(signature)

    # encode transaction data
    if r == 0 and s == 0:
        # null address
        return '0x' + '0' * 40
    elif v in (27, 28):
        chain_id = None
    elif v >= 37:
        chain_id = binary_utils.get_signature_network_id(signature)
        if chain_id is None:
            raise Exception('could not parse chain_id')
        v = v - chain_id * 2 - 8
        assert v in (27, 28)
    else:
        raise Exception('invalid v value')
    if (
        r >= binary_utils.signature_utils.secp256k1_utils.N
        or s >= binary_utils.signature_utils.secp256k1_utils.N
        or r == 0
        or s == 0
    ):
        raise Exception('invalid signature values')

    # get public key
    rlp_transaction = transaction_serialize.serialize_unsigned_transaction(
        transaction,
        chain_id=chain_id,
    )
    message_hash = binary_utils.keccak(rlp_transaction)
    public_key = binary_utils.recover_signer_public_key(
        message_hash=message_hash,
        signature=(v, r, s),
    )

    # convert public key to address
    sender = '0x' + binary_utils.keccak(public_key)[-40:]
    return sender


def is_transaction_signed(transaction: typing.Mapping[str, typing.Any]) -> bool:
    """return whether transaction is signed"""

    return (
        transaction.get('v') is not None
        and transaction.get('r') is not None
        and transaction.get('s') is not None
    )
