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


def get_created_address(
    sender: spec.Address,
    nonce: int | None = None,
    *,
    salt: str | None = None,
    init_code: spec.HexData | None = None,
) -> spec.Address:
    """return address created by EVM opcodes CREATE or CREATE2

    see https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1014.md
    see https://ethereum.stackexchange.com/a/761
    """

    if nonce is not None:
        # create
        data: str | bytes = binary_utils.rlp_encode(
            (sender, nonce), str_mode='hex'
        )
    elif salt is not None and init_code is not None:
        # create2
        data = (
            binary_utils.binary_convert('0xff', 'raw_hex')
            + binary_utils.binary_convert(sender, 'raw_hex')
            + binary_utils.binary_convert(salt, 'raw_hex')
            + binary_utils.binary_convert(
                binary_utils.keccak(init_code), 'raw_hex'
            )
        )
    else:
        raise Exception('specify either {nonce} or {salt, init_code}')

    result = binary_utils.keccak(data, output_format='prefix_hex')
    result = '0x' + result[26:]

    return result


def get_address_checksum(address: spec.Address) -> spec.Address:
    """return checksummed version of address str

    - adapted from eth_utils.to_checksum_address()
    """

    # validate address
    address_format = binary_utils.get_binary_format(address)
    if address_format not in ['prefix_hex', 'raw_hex']:
        raise Exception('checksum only relevant to hex formatted addresses')
    address = binary_utils.binary_convert(address, 'raw_hex')

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
        return binary_utils.binary_convert(raw_checksum, 'prefix_hex')
    else:
        raise Exception('checksum only relevant to hex formatted addresses')
