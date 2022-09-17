from __future__ import annotations

import typing

from ctc import spec
from . import format_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


@typing.overload
def keccak(
    data: spec.GenericBinaryData,
    output_format: Literal['integer'],
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> int:
    ...


@typing.overload
def keccak(
    data: spec.GenericBinaryData,
    output_format: Literal['binary'],
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> bytes:
    ...


@typing.overload
def keccak(
    data: spec.GenericBinaryData,
    output_format: Literal['prefix_hex', 'raw_hex', None] = 'prefix_hex',
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> str:
    ...


def keccak(
    data: spec.GenericBinaryData,
    output_format: typing.Optional[spec.BinaryFormat] = 'prefix_hex',
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> spec.GenericBinaryData:
    """return keccack-256 hash of hex or binary data"""

    # test that data is not a textual input
    if isinstance(data, str) and data != '0x':
        try:
            int(data, 16)
        except ValueError:
            raise Exception(
                'for text data, use keccak_text() instead of keccak()'
            )

    # determine library
    if library is None:
        try:
            import sha3  # type: ignore

            library = 'pysha3'

        except ImportError:
            library = 'pycryptodome'

    # convert data to binary
    data = format_utils.binary_convert(data, 'binary')

    if library == 'pysha3':
        import sha3

        binary = sha3.keccak_256(data).digest()
    elif library == 'pycryptodome':
        from Crypto.Hash import keccak as f_keccak

        binary = f_keccak.new(digest_bits=256, data=data).digest()
    else:
        raise Exception(
            'must choose valid library, either \'pysha3\' or \'pycryptodome\''
        )

    return format_utils.binary_convert(binary, output_format)


@typing.overload
def keccak_text(
    text: typing.Union[str, bytes],
    output_format: Literal['integer'],
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> int:
    ...


@typing.overload
def keccak_text(
    text: typing.Union[str, bytes],
    output_format: Literal['binary'],
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> bytes:
    ...


@typing.overload
def keccak_text(
    text: typing.Union[str, bytes],
    output_format: Literal['prefix_hex', 'raw_hex'] = 'prefix_hex',
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> str:
    ...


def keccak_text(
    text: typing.Union[str, bytes],
    output_format: spec.BinaryFormat = 'prefix_hex',
    *,
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> spec.GenericBinaryData:
    """return keccack-256 hash of text"""

    if isinstance(text, str):
        text = text.encode()

    return keccak(text, output_format=output_format, library=library)
