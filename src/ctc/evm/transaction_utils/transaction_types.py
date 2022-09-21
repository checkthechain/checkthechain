from __future__ import annotations

import typing

from ctc import spec
from .. import binary_utils


def standardize_transaction(
    transaction: typing.Mapping[str, typing.Any]
) -> typing.Mapping[str, typing.Any]:
    """return standardized version of transaction

    - convert any camelcase keys or non-standard keys to single format
    - fill in missing keys
    """

    standardized = {}
    for key, value in transaction.items():
        if key in spec.transaction_keys_standardized:
            key = spec.transaction_keys_standardized[key]
        standardized[key] = value

    if 'input' not in standardized:
        standardized['input'] = bytes()
    if (
        'max_priority_fee_per_gas' in standardized
        and 'access_list' not in standardized
    ):
        standardized['access_list'] = []

    return standardized


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
    transaction_or_type: typing.Mapping[str, typing.Any] | spec.Data,
    *,
    signed: bool,
) -> tuple[str, ...]:
    """return list of keys that are used by a given transaction type"""

    transaction_type = get_transaction_type(transaction_or_type)

    # get keys
    if transaction_type == 0:
        keys: tuple[str, ...] = spec.transaction_keys_legacy
    elif transaction_type == 1:
        keys = spec.transaction_keys_eip2930
    elif transaction_type == 2:
        keys = spec.transaction_keys_eip1559
    else:
        raise Exception('unknown transaction type: ' + str(transaction_type))

    # remove signature keys if unsigned
    if not signed:
        keys = tuple(key for key in keys if key not in ('v', 'r', 's'))

    return keys
