from __future__ import annotations

import typing

from ctc import spec
from .. import formats

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


def pack_vrs(
    *,
    v: spec.Data,
    r: spec.Data,
    s: spec.Data,
    mode: Literal['transaction', 'ecdsa'],
) -> str:

    v_bytes = formats.convert(v, 'binary', n_bytes=1)
    r_bytes = formats.convert(r, 'binary', n_bytes=32)
    s_bytes = formats.convert(s, 'binary', n_bytes=32)

    if mode == 'ecdsa':
        signature = r_bytes + s_bytes + v_bytes
    elif mode == 'transaction':
        delimiter = bytes.fromhex('a0')
        signature = v_bytes + delimiter + r_bytes + delimiter + s_bytes
    else:
        raise Exception('unknown vrs packing mode: ' + str(mode))

    return formats.convert(signature, 'prefix_hex')


def unpack_vrs(signature: spec.Data) -> tuple[int, int, int]:

    bytes_signature = formats.convert(signature, 'binary')

    if len(bytes_signature) == 65:
        r = bytes_signature[:32]
        s = bytes_signature[32:64]
        v = bytes_signature[64:]
    elif len(bytes_signature) == 67:
        v = bytes_signature[:1]
        r = bytes_signature[2:34]
        s = bytes_signature[35:]
    else:
        raise Exception('signature format unrecognized')

    return (
        formats.convert(v, 'integer'),
        formats.convert(r, 'integer'),
        formats.convert(s, 'integer'),
    )


def vrs_to_network_id(*, v: int, r: int, s: int) -> int | None:
    """adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/transactions.py#L93"""
    if r == 0 and s == 0:
        return v
    elif v in (27, 28):
        return None
    else:
        return ((v - 1) // 2) - 17
