from __future__ import annotations

import codecs
import typing

from ctc import spec


def get_binary_format(data: spec.GenericBinaryData) -> spec.BinaryFormat:
    """return binary format of input data"""
    if isinstance(data, bytes):
        return 'binary'
    elif isinstance(data, str):
        if data.startswith('0x'):
            return 'prefix_hex'
        else:
            return 'raw_hex'
    elif isinstance(data, int):
        return 'integer'
    else:
        raise Exception('could not detect format')


def get_binary_n_bytes(data: spec.GenericBinaryData) -> int:
    """return number of bytes in input data"""

    if isinstance(data, bytes):
        return len(data)
    elif isinstance(data, str):
        if len(data) % 2 != 0:
            raise Exception('hex data must have even number of characters')
        if data.startswith('0x'):
            return int(len(data) / 2) - 1
        else:
            return int(len(data) / 2)
    elif isinstance(data, int):
        # adapted from https://stackoverflow.com/a/30375198
        if data < 0:
            raise Exception('only positive integers allowed')
        return (data.bit_length() + 7) // 8
    else:
        raise Exception('unknown data type: ' + str(data))


#
# # binary data manipulation
#


def text_to_binary(
    text: str,
    output_format: typing.Optional[spec.BinaryFormat] = None,
) -> spec.GenericBinaryData:
    """convert text to binary data"""
    return binary_convert(text.encode(), output_format)


def binary_to_text(binary: spec.GenericBinaryData) -> str:
    """convert binary data to text"""
    return codecs.decode(binary_convert(binary, 'binary'))


@typing.overload
def binary_convert(
    data: spec.GenericBinaryData,
    output_format: typing.Literal['binary'],
    *,
    n_bytes: int | None = None,
    keep_leading_0: bool | None = None,
) -> bytes:
    ...


@typing.overload
def binary_convert(
    data: spec.GenericBinaryData,
    output_format: typing.Literal['integer'],
    *,
    n_bytes: int | None = None,
    keep_leading_0: bool | None = None,
) -> int:
    ...


@typing.overload
def binary_convert(
    data: spec.GenericBinaryData,
    output_format: typing.Optional[typing.Literal['prefix_hex', 'raw_hex']],
    *,
    n_bytes: int | None = None,
    keep_leading_0: bool | None = None,
) -> str:
    ...


def binary_convert(
    data: spec.GenericBinaryData,
    output_format: typing.Optional[spec.BinaryFormat] = None,
    *,
    n_bytes: int | None = None,
    keep_leading_0: bool | None = None,
) -> spec.GenericBinaryData:
    """convert {hex str or bytes} into {hex str or bytes}

    function should not be used with general text data

    ## Data Types
    - 'prefix_hex': hex str with 0x prefix included
    - 'raw_hex': hex str without 0x prefix included
    - 'binary': bytes

    :data: binary data
    :output_format: str name of output format
    """

    if output_format is None:
        output_format = 'prefix_hex'

    if isinstance(data, str):
        if data.startswith('0x'):
            raw_data = data[2:]
        else:
            raw_data = data

        if n_bytes is not None and len(raw_data) / 2 != n_bytes:
            raise Exception('data does not have target length')

        if output_format == 'prefix_hex':
            return '0x' + raw_data
        elif output_format == 'raw_hex':
            return raw_data
        elif output_format == 'binary':
            if len(raw_data) % 2 == 1:
                raw_data = '0' + raw_data
            return bytes.fromhex(raw_data)
        elif output_format == 'integer':
            return int(data, 16)
        else:
            raise Exception('invalid output_format: ' + str(output_format))

    elif isinstance(data, bytes):

        if n_bytes is not None and len(data) != n_bytes:
            raise Exception('data does not have target length')

        if output_format == 'binary':
            return data
        elif output_format == 'prefix_hex':
            return '0x' + data.hex()
        elif output_format == 'raw_hex':
            return data.hex()
        elif output_format == 'integer':
            return int.from_bytes(data, 'big')
        else:
            raise Exception('invalid output_format: ' + str(output_format))

    elif isinstance(data, int):

        if data < 0:
            raise Exception('only positive integers allowed')

        if output_format == 'integer':

            return data

        else:

            if keep_leading_0 is None:
                keep_leading_0 = True
            if n_bytes is None:
                n_bytes = get_binary_n_bytes(data)
            as_bytes = data.to_bytes(n_bytes, 'big')

            if output_format == 'binary':
                return as_bytes
            elif output_format in ['prefix_hex', 'raw_hex']:
                as_hex = as_bytes.hex()
                if not keep_leading_0:
                    as_hex = as_hex.lstrip('0')
                    if data == 0:
                        as_hex = '0'
                if output_format == 'prefix_hex':
                    return '0x' + as_hex
                else:
                    return as_hex
            else:
                raise Exception('invalid output_format: ' + str(output_format))

    else:

        raise Exception('unknown input data format: ' + str(type(data)))
