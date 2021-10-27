import sha3

from . import format_utils


def keccak(data, output_format='prefix_hex'):
    """return keccack-256 hash of hex or binary data"""
    data = format_utils.convert_binary_format(data, 'binary')
    binary = sha3.keccak_256(data).digest()
    return format_utils.convert_binary_format(binary, output_format)


def keccak_text(text, output_format='prefix_hex'):
    """return keccack-256 hash of text"""
    return keccak(text.encode(), output_format)

