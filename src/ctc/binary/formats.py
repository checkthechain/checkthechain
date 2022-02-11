from __future__ import annotations

import typing

from ctc import spec


def get_binary_format(data: spec.BinaryInteger) -> spec.BinaryFormat:
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


def get_binary_n_bytes(data: spec.BinaryInteger) -> int:

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


@typing.overload
def convert(
    data: spec.BinaryInteger,
    output_format: typing.Literal['binary'],
) -> bytes:
    ...


@typing.overload
def convert(
    data: spec.BinaryInteger,
    output_format: typing.Literal['integer'],
) -> int:
    ...


@typing.overload
def convert(
    data: spec.BinaryInteger,
    output_format: typing.Optional[typing.Literal['prefix_hex', 'raw_hex']],
) -> str:
    ...


def convert(
    data: spec.BinaryInteger,
    output_format: typing.Optional[spec.BinaryFormat] = None,
) -> spec.BinaryInteger:
    """convert {hex str or bytes} into {hex str or bytes}

    function should not be used with general text data

    ## Data Types
    - 'prefix_hex': hex str with 0x prefix included
    - 'raw_hex': hex str without 0x prefix included
    - 'binary': bytes
    """

    if output_format is None:
        output_format = 'prefix_hex'

    if isinstance(data, str):
        if data.startswith('0x'):
            raw_data = data[2:]
        else:
            raw_data = data

        if output_format == 'prefix_hex':
            return '0x' + raw_data
        elif output_format == 'raw_hex':
            return raw_data
        elif output_format == 'binary':
            return bytes.fromhex(raw_data)
        elif output_format == 'integer':
            return int(data, 16)
        else:
            raise Exception('invalid output_format: ' + str(output_format))

    elif isinstance(data, bytes):

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

        n_bytes = get_binary_n_bytes(data)

        if output_format == 'binary':
            return data.to_bytes(n_bytes, 'big')
        elif output_format == 'prefix_hex':
            return hex(data)
        elif output_format == 'raw_hex':
            return hex(data)[2:]
        elif output_format == 'integer':
            return data
        else:
            raise Exception('invalid output_format: ' + str(output_format))

    else:

        raise Exception('unknown input data format: ' + str(type(data)))


def add_binary_pad(
    data: spec.BinaryInteger,
    pad_side: typing.Literal['left', 'right', None] = None,
    padded_size: int = None,
) -> spec.BinaryInteger:
    """add pad of zeros to left or right side of binary data"""

    # default arguments
    if pad_side is None:
        pad_side = 'left'
    if padded_size is None:
        padded_size = 32

    # determine pad bytes
    binary_format = get_binary_format(data)
    data_bytes = get_binary_n_bytes(data)
    if padded_size < data_bytes:
        raise Exception('pad size too small for data')
    pad_bytes = padded_size - data_bytes

    if binary_format == 'binary':

        data = typing.cast(bytes, data)

        if pad_side == 'left':
            return bytes(0) * pad_bytes + data
        elif pad_side == 'right':
            return data + bytes(0) * pad_bytes
        else:
            raise Exception('invalid pad side: ' + str(pad_side))

    elif binary_format == 'prefix_hex':

        data = typing.cast(str, data)

        if pad_side == 'left':
            return '0x' + '0' * 2 * pad_bytes + data[2:]
        elif pad_side == 'right':
            return data + '0' * 2 * pad_bytes
        else:
            raise Exception('invalid pad side: ' + str(pad_side))

    elif binary_format == 'raw_hex':

        data = typing.cast(str, data)

        if pad_side == 'left':
            return '0' * 2 * pad_bytes + data
        elif pad_side == 'right':
            return data + '0' * 2 * pad_bytes
        else:
            raise Exception('invalid pad side: ' + str(pad_side))

    else:

        raise Exception('invalid binary format: ' + str(binary_format))


def match_format(
    format_this: spec.BinaryInteger,
    like_this: spec.BinaryInteger,
    match_pad: bool = False,
) -> spec.BinaryInteger:
    """

    will only match left pads, because pad size cannot be reliably determined
    """

    output_format = get_binary_format(like_this)
    output = convert(data=format_this, output_format=output_format)

    if match_pad:
        padded_size = get_binary_n_bytes(like_this)
        output = add_binary_pad(output, padded_size=padded_size)

    return output

