"""
see
- https://eth.wiki/en/fundamentals/rlp
- https://ethereum.org/en/developers/docs/data-structures-and-encoding/rlp/
"""
from __future__ import annotations

import typing

from ctc import spec
from . import formats

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


def rlp_decode(data: spec.BinaryData) -> typing.Any:
    try:
        import rlp
    except ImportError:
        raise Exception(
            'the rlp package is required for this feature, try `pip install rlp`'
        )

    binary_data = formats.convert(data, 'binary')

    return rlp.decode(binary_data)


@typing.overload
def rlp_encode(
    item: typing.Any,
    output_format: typing.Literal['binary'],
    *,
    str_mode: Literal['auto', 'text', 'hex'] | None = None,
) -> bytes:
    ...


@typing.overload
def rlp_encode(
    item: typing.Any,
    output_format: typing.Literal['integer'],
    *,
    str_mode: Literal['auto', 'text', 'hex'] | None = None,
) -> int:
    ...


@typing.overload
def rlp_encode(
    item: typing.Any,
    output_format: typing.Literal['prefix_hex', 'raw_hex'] = 'prefix_hex',
    *,
    str_mode: Literal['auto', 'text', 'hex'] | None = None,
) -> str:
    ...


def rlp_encode(
    item: typing.Any,
    output_format: spec.BinaryFormat = 'prefix_hex',
    *,
    str_mode: Literal['auto', 'text', 'hex'] | None = 'auto',
) -> spec.BinaryInteger:
    """str_mode specifies how str values should be interpreted"""

    if isinstance(item, int):
        if item == 0:
            item = bytes()
        else:
            item = formats.convert(item, 'binary')

    if isinstance(item, (tuple, list)):
        output = rlp_encode_list(item, str_mode=str_mode)
    elif isinstance(item, bytes):
        output = rlp_encode_bytes(item)
    elif isinstance(item, str):
        output = rlp_encode_str(item, str_mode=str_mode)
    else:
        raise Exception('cannot rlp encode items of type ' + str(type(item)))

    return formats.convert(output, output_format)


def rlp_encode_bytes(data: bytes) -> bytes:

    data = formats.convert(data, 'binary')

    length = len(data)
    if length == 0:
        return bytes.fromhex('80')
    elif length == 1 and data <= bytes.fromhex('7f'):
        return data
    elif length <= 55:
        prefix = 128 + length
        return formats.convert(prefix, 'binary') + data
    else:
        length_as_bytes = formats.convert(length, 'binary')
        prefix = 183 + len(length_as_bytes)
        return formats.convert(prefix, 'binary') + length_as_bytes + data


def rlp_encode_list(
    items: typing.Sequence[typing.Any],
    str_mode: Literal['text', 'hex'] | None = None,
) -> bytes:

    encoded_items = [
        rlp_encode(item, str_mode=str_mode, output_format='binary')
        for item in items
    ]
    item_lengths = [len(encoded_item) for encoded_item in encoded_items]
    total_payload_length = sum(item_lengths)

    if total_payload_length <= 55:
        prefix = formats.convert(192 + total_payload_length, 'binary')
        output = prefix
        for item in encoded_items:
            output = output + item
        return output

    else:
        bytes_of_length = formats.convert(total_payload_length, 'binary')
        prefix_int = 248 + len(bytes_of_length)
        output = formats.convert(prefix_int, 'binary') + bytes_of_length
        for item in encoded_items:
            output = output + item
        return output


def rlp_encode_str(
    item: str,
    str_mode: Literal['auto', 'text', 'hex'] | None,
) -> bytes:

    if str_mode == 'auto':
        if item.startswith('0x'):
            str_mode = 'hex'
        else:
            str_mode = 'text'

    if str_mode == 'text':
        as_bytes = item.encode()
    elif str_mode == 'hex':
        as_bytes = formats.convert(item, 'binary')
    else:
        raise Exception('unknown str mode: ' + str(str_mode))

    return rlp_encode_bytes(as_bytes)
