from __future__ import annotations

from ctc import spec
from .. import binary_utils
from . import transaction_serialize


def hash_unsigned_transaction(
    transaction: spec.TransactionData,
    *,
    chain_id: int | None = None,
) -> spec.Data:
    """compute hash of unsigned transaction"""

    serialized = transaction_serialize.serialize_unsigned_transaction(
        transaction,
        chain_id=chain_id,
    )
    return binary_utils.keccak(serialized)


def hash_signed_transaction(transaction: spec.TransactionData) -> spec.Data:
    """compute hash of signed transaction"""

    serialized = transaction_serialize.serialize_signed_transaction(transaction)
    return binary_utils.keccak(serialized)
