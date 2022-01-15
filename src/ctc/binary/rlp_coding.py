"""
see https://eth.wiki/en/fundamentals/rlp
"""

from . import formats


def rlp_encode(data, output_format='prefix_hex'):
    import rlp  # type: ignore

    rlp_data = rlp.encode(data)
    return formats.convert(rlp_data, output_format)


def rlp_decode(data):
    import rlp  # type: ignore

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

