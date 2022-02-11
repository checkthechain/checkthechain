from __future__ import annotations

import typing
from typing_extensions import Literal

from ctc import spec
from . import formats


@typing.overload
def keccak(
    data: spec.BinaryInteger,
    output_format: Literal['integer'],
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> int:
    ...


@typing.overload
def keccak(
    data: spec.BinaryInteger,
    output_format: Literal['binary'],
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> bytes:
    ...


@typing.overload
def keccak(
    data: spec.BinaryInteger,
    output_format: Literal['prefix_hex', 'raw_hex', None],
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> str:
    ...


def keccak(
    data: spec.BinaryInteger,
    output_format: typing.Optional[spec.BinaryFormat] = 'prefix_hex',
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> spec.BinaryInteger:
    """return keccack-256 hash of hex or binary data"""

    # determine library
    if library is None:
        try:
            import sha3  # type: ignore

            library = 'pysha3'

        except ImportError:
            library = 'pycryptodome'

    # convert data to binary
    data = formats.convert(data, 'binary')

    if library == 'pysha3':
        import sha3  # type: ignore

        binary = sha3.keccak_256(data).digest()
    elif library == 'pycryptodome':
        from Crypto.Hash import keccak as f_keccak

        binary = f_keccak.new(digest_bits=256, data=data).digest()
    else:
        raise Exception(
            'must choose valid library, either \'pysha3\' or \'pycryptodome\''
        )

    return formats.convert(binary, output_format)


@typing.overload
def keccak_text(
    text: str,
    output_format: Literal['integer'],
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> int:
    ...


@typing.overload
def keccak_text(
    text: str,
    output_format: Literal['binary'],
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> bytes:
    ...


@typing.overload
def keccak_text(
    text: str,
    output_format: Literal['prefix_hex', 'raw_hex'] = 'prefix_hex',
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> str:
    ...


def keccak_text(
    text: str,
    output_format: spec.BinaryFormat = 'prefix_hex',
    library: typing.Optional[typing.Literal['pysha3', 'pycryptodome']] = None,
) -> spec.BinaryInteger:
    """return keccack-256 hash of text"""
    return keccak(text.encode(), output_format=output_format, library=library)

