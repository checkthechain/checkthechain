from __future__ import annotations

import typing

from ctc import binary
from ctc import spec


def is_address_str(some_str: str) -> bool:
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
    # see https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1014.md
    # see https://ethereum.stackexchange.com/a/761
    if nonce is not None:
        # create
        sender_binary = binary.convert(sender, 'binary')
        data = binary.rlp_encode([sender_binary, nonce])
    elif salt is not None and init_code is not None:
        # create2
        data = (
            binary.convert('0xff', 'raw_hex')
            + binary.convert(sender, 'raw_hex')
            + binary.convert(salt, 'raw_hex')
            + binary.convert(binary.keccak(init_code), 'raw_hex')
        )
    else:
        raise Exception('specify either {nonce} or {salt, init_code}')

    result = binary.keccak(data, output_format='prefix_hex')
    result = '0x' + result[26:]

    return result


def create_hash_preview(
    hash_data: str,
    *,
    show_start: bool = True,
    show_end: bool = True,
    include_0x: bool = True,
    n_chars: int = 6,
    n_chars_start: int | None = None,
    n_chars_end: int | None = None,
) -> str:

    if not include_0x and hash_data[:2] == '0x':
        hash_data = hash_data[2:]

    if n_chars_start is None:
        n_chars_start = n_chars
        if include_0x:
            n_chars_start += 2
    if n_chars_end is None:
        n_chars_end = n_chars

    preview = '...'
    if show_start:
        preview = hash_data[:n_chars_start] + preview
    if show_end:
        preview = preview + hash_data[:-n_chars_end]

    return preview


def get_address_checksum(address: spec.Address) -> spec.Address:
    """

    - adapted from eth_utils.to_checksum_address()
    """

    # validate address
    address_format = binary.get_binary_format(address)
    if address_format not in ['prefix_hex', 'raw_hex']:
        raise Exception('checksum only relevant to hex formatted addresses')
    address = binary.convert(address, 'raw_hex')

    # compute address hash
    address_hash = binary.keccak_text(
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
        return binary.convert(raw_checksum, 'prefix_hex')
    else:
        raise Exception('checksum only relevant to hex formatted addresses')


def create_reverse_address_map(
    address_map: typing.Mapping[str, spec.Address],
    *,
    include_lower: bool = True,
    include_checksum: bool = True,
) -> dict[spec.Address, str]:
    if not include_lower and not include_checksum:
        raise Exception(
            'must include lower case addresses and/or checksum addresses'
        )

    reverse_map = {}
    for name, address in address_map.items():
        if include_lower:
            reverse_map[address.lower()] = name
        if include_checksum:
            reverse_map[get_address_checksum(address)] = name

    return reverse_map
