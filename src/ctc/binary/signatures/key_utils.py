from __future__ import annotations

from ctc import spec

from .. import formats
from .. import hashes
from . import secp256k1_utils


def private_key_to_public_key(private_key: spec.Data) -> str:
    binary_private_key = formats.convert(private_key, 'binary')
    as_tuple = secp256k1_utils.privtopub(binary_private_key)
    return public_key_tuple_to_hex(as_tuple)


def private_key_to_address(private_key: spec.Data) -> spec.Address:
    public_key = private_key_to_public_key(private_key)
    return public_key_to_address(public_key)


def public_key_to_address(
    public_key: tuple[int, int] | spec.Data
) -> spec.Address:
    as_hex = public_key_tuple_to_hex(public_key)
    hash = hashes.keccak(as_hex, 'binary')
    address = hash[-20:]
    return formats.convert(address, 'prefix_hex')


def public_key_tuple_to_hex(public_key: tuple[int, int] | spec.Data) -> str:

    if isinstance(public_key, tuple):
        if len(public_key) == 2:
            x, y = public_key
            as_bytes = x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
            return formats.convert(as_bytes, 'prefix_hex')
        else:
            raise Exception('unknown pubilc key format')

    else:
        return formats.convert(
            public_key, output_format='prefix_hex', n_bytes=64
        )
