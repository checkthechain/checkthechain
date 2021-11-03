#
# # binary data reading
#


def get_binary_format(data):
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


def get_binary_n_bytes(data):

    if isinstance(data, bytes):
        return len(data)
    elif isinstance(data, str):
        if data.startswith('0x'):
            return len(data) / 2 - 1
        else:
            return len(data) / 2
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


def convert_binary_format(
    data, output_format=None, padded_size=None, pad_side=None
):
    """convert {hex str or bytes} into {hex str or bytes}

    function should not be used with general text data

    ## Data Types
    - 'prefix_hex': hex str with 0x prefix included
    - 'raw_hex': hex str without 0x prefix included
    - 'binary': bytes
    """

    if output_format is None:
        output_format = 'prefix_hex'

    # add pad
    if padded_size is not None or pad_side is not None:
        data = add_binary_pad(data, padded_size=padded_size, pad_side=pad_side)

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

        if padded_size is not None:
            n_bytes = padded_size
        else:
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


def add_binary_pad(data, pad_side=None, padded_size=None):
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

        if pad_side == 'left':
            return bytes(0) * pad_bytes + data
        elif pad_side == 'right':
            return data + bytes(0) * pad_bytes
        else:
            raise Exception('invalid pad side: ' + str(pad_side))

    elif binary_format == 'prefix_hex':

        if pad_side == 'left':
            return '0x' + '0' * 2 * pad_bytes + data[2:]
        elif pad_side == 'right':
            return data + '0' * 2 * pad_bytes
        else:
            raise Exception('invalid pad side: ' + str(pad_side))

    elif binary_format == 'raw_hex':

        if pad_side == 'left':
            return '0' * 2 * pad_bytes + data
        elif pad_side == 'right':
            return data + '0' * 2 * pad_bytes
        else:
            raise Exception('invalid pad side: ' + str(pad_side))

    else:

        raise Exception('invalid binary format: ' + str(binary_format))


def match_binary_format(format_this, like_this, match_pad=False):
    """

    will only match left pads, because pad size cannot be reliably determined
    """

    output_format = get_binary_format(like_this)

    if match_pad:
        padded_size = get_binary_n_bytes(like_this)
    else:
        padded_size = None

    return convert_binary_format(
        data=format_this,
        output_format=output_format,
        padded_size=padded_size,
    )

