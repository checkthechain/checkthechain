from __future__ import annotations

import typing

from ctc import spec
from .. import binary_utils


def get_transaction_type(
    transaction_or_type: spec.Data | typing.Mapping[str, typing.Any]
) -> int:
    """get transaction type"""

    if isinstance(transaction_or_type, (int, str, bytes)):
        # if type provided directly, convert to int
        return binary_utils.binary_convert(transaction_or_type, 'integer')

    elif isinstance(transaction_or_type, dict):
        transaction = transaction_or_type

        # if type explicitly provided, use it
        if 'type' in transaction:
            return binary_utils.binary_convert(transaction['type'], 'integer')

        # otherwise, infer type based on fields
        if 'max_fee_per_gas' in transaction:
            return 2
        if 'access_list' in transaction or 'accessList' in transaction:
            return 1
        else:
            return 0

    else:
        raise Exception('unknown transaction format')


def get_transaction_type_name(
    transaction_or_type: typing.Mapping[str, typing.Any] | spec.Data
) -> str:
    """get transaction type name"""

    transaction_type = get_transaction_type(transaction_or_type)

    # return name
    if transaction_type == 0:
        return 'legacy'
    elif transaction_type == 1:
        return 'eip2930'
    elif transaction_type == 2:
        return 'eip1559'
    else:
        raise Exception('unknown transaction type: ' + str(transaction_type))


def get_transaction_type_keys(
    transaction: typing.Mapping[str, typing.Any],
    *,
    signed: bool,
) -> tuple[str, ...]:
    """return list of keys that are used by a given transaction type"""

    transaction_type = get_transaction_type(transaction)

    # determine whether camelcase
    if transaction_type in [1, 2]:
        if 'accessList' in transaction:
            snake = False
        elif 'access_list' in transaction:
            snake = True
        else:
            raise Exception('transaction does not specify access_list or accessList')
    elif transaction_type == 0:
        snake = 'chain_id' in transaction
    else:
        raise Exception('unknown transaction type: ' + str(transaction_type))

    # get keys
    if transaction_type == 0:
        keys: tuple[str, ...] = spec.transaction_keys_legacy
    elif transaction_type == 1 and snake:
        keys = spec.transaction_keys_eip2930
    elif transaction_type == 1 and not snake:
        keys = spec.transaction_keys_eip2930_camel
    elif transaction_type == 2 and snake:
        keys = spec.transaction_keys_eip1559
    elif transaction_type == 2 and not snake:
        keys = spec.transaction_keys_eip1559_camel
    else:
        raise Exception('unknown transaction type: ' + str(transaction_type))

    # remove signature keys if unsigned
    if not signed:
        keys = tuple(key for key in keys if key not in ('v', 'r', 's'))

    return keys
