from __future__ import annotations

from ctc import spec
from .. import binary_utils
from . import transaction_types


def serialize_unsigned_transaction(
    transaction: spec.TransactionData,
    *,
    chain_id: int | None = None,
) -> spec.PrefixHexData:
    """serialize unsigned transaction"""

    # collect keys for transaction type
    type = transaction_types.get_transaction_type(transaction)
    keys = transaction_types.get_transaction_type_keys(type, signed=False)

    # represent as list
    as_list = [transaction[key] for key in keys]  # type: ignore

    # add EIP-155 chain_id
    if type == 0:
        if chain_id is None and transaction.get('chain_id') is not None:
            chain_id = binary_utils.binary_convert(transaction.get('chain_id'), 'integer')  # type: ignore
        if chain_id is not None:
            as_list.append(chain_id)
            as_list.append(0)
            as_list.append(0)

    # get transaction type prefix
    if type == 0:
        prefix = '0x'
    elif type == 1:
        prefix = '0x01'
    elif type == 2:
        prefix = '0x02'
    else:
        raise Exception('unknown transaction type: ' + str(type))

    return prefix + binary_utils.rlp_encode(as_list, 'raw_hex')


def serialize_signed_transaction(
    transaction: spec.TransactionData,
) -> spec.PrefixHexData:
    """serialize signed transaction"""

    # collect keys for transaction type
    type = transaction_types.get_transaction_type(transaction)
    keys = transaction_types.get_transaction_type_keys(type, signed=True)

    # get list of fields
    as_list = [transaction[key] for key in keys]  # type: ignore

    # get transaction type prefix
    if type == 0:
        prefix = '0x'
    elif type == 1:
        prefix = '0x01'
    elif type == 2:
        prefix = '0x02'
    else:
        raise Exception('unknown transaction type: ' + str(type))

    # encode as rlp
    return prefix + binary_utils.rlp_encode(as_list, 'raw_hex')
