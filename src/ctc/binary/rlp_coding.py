"""
see https://eth.wiki/en/fundamentals/rlp
"""
from __future__ import annotations

import typing

from ctc import spec
from . import formats


def rlp_encode_int(integer: int) -> spec.PrefixHexData:
    if integer == 0:
        return '0x80'
    elif integer <= 127:
        encoded = formats.convert(integer, 'raw_hex')
        if len(encoded) == 1:
            encoded = '0' + encoded
        return '0x' + encoded
    else:
        integer_hex = formats.convert(integer, 'raw_hex')
        if len(integer_hex) % 2 == 1:
            integer_hex = '0' + integer_hex
        integer_bytes = int(len(integer_hex) / 2)
        return formats.convert(128 + integer_bytes, 'prefix_hex') + integer_hex


def rlp_encode_address(address):
    return '0x94' + formats.convert(address, 'raw_hex')


def rlp_encode_address_nonce_tuple(address, nonce) -> spec.PrefixHexData:
    rlp_address = rlp_encode_address(address)[2:]
    rlp_integer = rlp_encode_int(nonce)[2:]
    data_len = int(len(rlp_address) / 2 + len(rlp_integer) / 2)

    if data_len <= 55:
        pre_offset = 192
    else:
        pre_offset = 247

    return (
        '0x'
        + formats.convert(pre_offset + data_len, 'raw_hex')
        + rlp_address
        + rlp_integer
    )


def rlp_encode(data: typing.Any) -> str:
    try:
        import rlp  # type: ignore
    except ImportError:
        raise Exception(
            'the rlp package is required for this feature, try `pip install rlp`'
        )

    rlp_data = rlp.encode(data)
    return formats.convert(rlp_data, 'prefix_hex')


def rlp_decode(data: spec.BinaryData) -> typing.Any:
    try:
        import rlp
    except ImportError:
        raise Exception(
            'the rlp package is required for this feature, try `pip install rlp`'
        )

    binary_data = formats.convert(data, 'binary')

    return rlp.decode(binary_data)


# def rlp_encode(input):
#    if isinstance(input, str):
#        if len(input) == 1 and ord(input) < 0x80:
#            return input
#        else:
#            return encode_length(len(input), 0x80) + input
#    elif isinstance(input, list):
#        output = ''
#        for item in input:
#            output += rlp_encode(item)
#        return encode_length(len(output), 0xC0) + output


# def encode_length(L, offset):
#    if L < 56:
#        return chr(L + offset)
#    elif L < 256 ** 8:
#        BL = to_binary(L)
#        return chr(len(BL) + offset + 55) + BL
#    else:
#        raise Exception("input too long")


# def to_binary(x):
#    if x == 0:
#        return ''
#    else:
#        return to_binary(int(x / 256)) + chr(x % 256)


##
## # decode
##
# def rlp_decode(input):
#    if len(input) == 0:
#        return
#    output = ''
#    (offset, dataLen, type) = decode_length(input)
#    if type is str:
#        output = str(substr(input, offset, dataLen))
#    elif type is list:
#        output = list(substr(input, offset, dataLen))
#    output + rlp_decode(substr(input, offset + dataLen))
#    return output


# def decode_length(input):
#    length = len(input)
#    if length == 0:
#        raise Exception("input is null")
#    prefix = ord(input[0])
#    if prefix <= 0x7F:
#        return (0, 1, str)
#    elif prefix <= 0xB7 and length > prefix - 0x80:
#        strLen = prefix - 0x80
#        return (1, strLen, str)
#    elif (
#        prefix <= 0xBF
#        and length > prefix - 0xB7
#        and length > prefix - 0xB7 + to_integer(substr(input, 1, prefix - 0xB7))
#    ):
#        lenOfStrLen = prefix - 0xB7
#        strLen = to_integer(substr(input, 1, lenOfStrLen))
#        return (1 + lenOfStrLen, strLen, str)
#    elif prefix <= 0xF7 and length > prefix - 0xC0:
#        listLen = prefix - 0xC0
#        return (1, listLen, list)
#    elif (
#        prefix <= 0xFF
#        and length > prefix - 0xF7
#        and length > prefix - 0xF7 + to_integer(substr(input, 1, prefix - 0xF7))
#    ):
#        lenOfListLen = prefix - 0xF7
#        listLen = to_integer(substr(input, 1, lenOfListLen))
#        return (1 + lenOfListLen, listLen, list)
#    else:
#        raise Exception("input don't conform RLP encoding form")


# def to_integer(b):
#    length = len(b)
#    if length == 0:
#        raise Exception("input is null")
#    elif length == 1:
#        return ord(b[0])
#    else:
#        return ord(substr(b, -1)) + to_integer(substr(b, 0, -1)) * 256


# def substr(s, beginning, length=None):
#    if length is None:
#        return s[beginning:]
#    else:
#        return s[beginning: length + 1]
