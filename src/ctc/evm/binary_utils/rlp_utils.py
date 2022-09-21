"""
see
- https://eth.wiki/en/fundamentals/rlp
- https://ethereum.org/en/developers/docs/data-structures-and-encoding/rlp/
"""
from __future__ import annotations

import typing

from ctc import spec
from . import format_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal

    # use recursive type once mypy#731 gets released
    # https://github.com/python/mypy/issues/731

    # RLPDecodeTypes = typing.Sequence[typing.Any] | typing.ExtendedBinaryFormat | None
    RLPDecodeTypes = typing.Any


#
# # encoder
#


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
) -> spec.GenericBinaryData:
    """encode data as RLP

    str_mode specifies how str values should be interpreted
    """

    if isinstance(item, int):
        if item == 0:
            item = bytes()
        else:
            item = format_utils.binary_convert(item, 'binary')

    if isinstance(item, (tuple, list)):
        output = _rlp_encode_list(item, str_mode=str_mode)
    elif isinstance(item, bytes):
        output = _rlp_encode_bytes(item)
    elif isinstance(item, str):
        output = _rlp_encode_str(item, str_mode=str_mode)
    else:
        raise Exception('cannot rlp encode items of type ' + str(type(item)))

    return format_utils.binary_convert(output, output_format)


def _rlp_encode_bytes(data: bytes) -> bytes:

    data = format_utils.binary_convert(data, 'binary')

    length = len(data)
    if length == 0:
        return bytes.fromhex('80')
    elif length == 1 and data <= bytes.fromhex('7f'):
        return data
    elif length <= 55:
        prefix = 128 + length
        return format_utils.binary_convert(prefix, 'binary') + data
    else:
        length_as_bytes = format_utils.binary_convert(length, 'binary')
        prefix = 183 + len(length_as_bytes)
        return (
            format_utils.binary_convert(prefix, 'binary')
            + length_as_bytes
            + data
        )


def _rlp_encode_list(
    items: typing.Sequence[typing.Any],
    str_mode: Literal['auto', 'text', 'hex'] | None = None,
) -> bytes:

    encoded_items = [
        rlp_encode(item, str_mode=str_mode, output_format='binary')
        for item in items
    ]
    item_lengths = [len(encoded_item) for encoded_item in encoded_items]
    total_payload_length = sum(item_lengths)

    if total_payload_length <= 55:
        prefix = format_utils.binary_convert(
            192 + total_payload_length, 'binary'
        )
        output = prefix
        for item in encoded_items:
            output = output + item
        return output

    else:
        bytes_of_length = format_utils.binary_convert(
            total_payload_length, 'binary'
        )
        prefix_int = 247 + len(bytes_of_length)
        output = (
            format_utils.binary_convert(prefix_int, 'binary') + bytes_of_length
        )
        for item in encoded_items:
            output = output + item
        return output


def _rlp_encode_str(
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
        as_bytes = format_utils.binary_convert(item, 'binary')
    else:
        raise Exception('unknown str mode: ' + str(str_mode))

    return _rlp_encode_bytes(as_bytes)


#
# # decoder
#


def rlp_decode(
    data: spec.Data,
    types: RLPDecodeTypes = None,
) -> typing.Any:
    """decode RLP data

    the types parameter determines how raw data will be decoded in python
    - types is one of:
        1. binary format name: prefix_hex, raw_hex, binary, integer, ascii
        2. list/tuple of binary format names, corresponding to items in rlp list
    """

    # convert any abi types to RLP types
    if types is not None:
        types = _process_rlp_types(types)

    data = format_utils.binary_convert(data, 'binary')
    decoded, remaining = _rlp_decode_chunk(data=data, types=types)
    if len(remaining) > 0:
        raise Exception('data contains extra bytes')
    return decoded


def _process_rlp_types(
    types: str | typing.Sequence[str],
) -> str | typing.Sequence[str]:

    allowed_types = [
        'prefix_hex',
        'raw_hex',
        'binary',
        'integer',
        'ascii',
        'bool',
    ]

    if isinstance(types, str):
        if types in allowed_types:
            return types
        elif types.startswith('int') and '[' not in types:
            return 'integer'
        elif types == 'string':
            return 'ascii'
        else:
            raise Exception('RLP type not understood: ' + str(types))
    else:
        return [_process_rlp_types(type) for type in types]  # type: ignore


def _rlp_decode_chunk(
    data: bytes,
    types: RLPDecodeTypes,
) -> tuple[typing.Any, bytes]:
    """decode next item chunk in rlp encoded data"""

    if len(data) == 0:
        raise Exception()

    first_byte = data[0]
    if first_byte <= 0xBF:
        return _rlp_decode_primitive_chunk(data, types=types)
    else:
        result = _rlp_decode_list_chunk(data, types=types)
        return result


def _rlp_decode_primitive_chunk(
    data: bytes,
    types: RLPDecodeTypes,
) -> tuple[typing.Any, bytes]:

    first_byte = data[0]

    if first_byte <= 0x7F:
        # data that is single byte less than or equal to 127

        decoded: typing.Any = first_byte.to_bytes(1, 'big')
        remaining = data[1:]

    elif first_byte <= 0xB7:
        # data with length between 0 and 55 bytes

        # get length
        length = first_byte - 0x80

        # get data
        start = 1
        end = 1 + length
        decoded = data[start:end]
        remaining = data[end:]

    elif first_byte <= 0xBF:
        # data longer than 55 bytes

        # get length length
        length_length = first_byte - 0xB7

        # get length
        start = 1
        end = 1 + length_length
        length = int.from_bytes(data[start:end], 'big')

        # get data
        start = 1 + length_length
        end = 1 + length_length + length
        decoded = data[start:end]
        remaining = data[end:]

    else:
        raise Exception('next item in data is not a primitive chunk')

    # convert
    if types is not None:
        if types == 'ascii':
            decoded = decoded.decode()
        elif types == 'bool':
            decoded = bool(decoded)
        else:
            decoded = format_utils.binary_convert(decoded, types)

    return decoded, remaining


def _rlp_decode_list_chunk(
    data: bytes,
    types: RLPDecodeTypes,
) -> tuple[list[typing.Any], bytes]:

    first_byte = data[0]

    if first_byte <= 0xBF:
        raise Exception('next item in data is not a list chunk')

    elif first_byte <= 0xF7:
        # list with total payload length between 0 and 55 bytes

        # get length
        length = first_byte - 0xC0

        # decode list
        start = 1
        end = 1 + length
        list_payload = data[start:end]

        if len(list_payload) != length:
            raise Exception('data is shorted than specified by header')

        remaining = data[end:]

    else:
        # list with payload longer than 55 bytes

        # get length length
        length_length = first_byte - 0xF7

        # get length
        start = 1
        end = 1 + length_length
        length = int.from_bytes(data[start:end], 'big')

        # decode list
        start = 1 + length_length
        end = 1 + length_length + length
        list_payload = data[start:end]

        if len(list_payload) != length:
            raise Exception('data is shorted than specified by header')

        remaining = data[end:]

    # decode each item of list payload
    output = []
    remaining_payload = list_payload
    index = 0
    while len(remaining_payload) > 0:

        # get type of item
        if isinstance(types, (list, tuple)):
            if index >= len(types):
                raise Exception(
                    'number of types does not match number of list items'
                )
            item_types = types[index]
        elif isinstance(types, str):
            item_types = types
        else:
            item_types = None

        # decode next item in list
        item, remaining_payload = _rlp_decode_chunk(
            remaining_payload,
            types=item_types,
        )
        output.append(item)
        index += 1

    return output, remaining
