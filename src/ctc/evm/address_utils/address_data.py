from __future__ import annotations

import typing

from ctc import spec
from .. import binary_utils

if typing.TYPE_CHECKING:
    from typing_extensions import TypeGuard


def is_address_str(some_str: typing.Any) -> TypeGuard[spec.Address]:
    """return whether input is an address str"""

    return (
        isinstance(some_str, str)
        and some_str.startswith('0x')
        and len(some_str) == 42
    )


def get_address_checksum(address: spec.Address) -> spec.Address:
    """return checksummed version of address str

    - adapted from eth_utils.to_checksum_address()
    """

    # validate address
    address_format = binary_utils.get_binary_format(address)
    if address_format not in ['prefix_hex', 'raw_hex']:
        raise Exception('checksum only relevant to hex formatted addresses')
    address = binary_utils.to_hex(address, prefix=False)

    # compute address hash
    address_hash = binary_utils.keccak_text(
        address.lower(),
        output_format='raw_hex',
    )

    # assemble checksum
    chars = []
    for address_char, hash_char in zip(address, address_hash):
        if int(hash_char, 16) > 7:
            chars.append(address_char.upper())
        else:
            chars.append(address_char.lower())
    raw_checksum = ''.join(chars)

    # convert to output format
    if address_format == 'raw_hex':
        return raw_checksum
    elif address_format == 'prefix_hex':
        return binary_utils.to_hex(raw_checksum)
    else:
        raise Exception('checksum only relevant to hex formatted addresses')
