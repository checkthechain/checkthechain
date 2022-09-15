from __future__ import annotations

import typing

from ctc import spec
from .. import format_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


def convert_vrs_tuple_type(
    vrs: tuple[spec.Data, spec.Data, spec.Data],
    output_format: spec.BinaryFormat,
) -> tuple[spec.Data, spec.Data, spec.Data]:
    v, r, s = vrs
    return (
        format_utils.convert(v, output_format),
        format_utils.convert(r, output_format),
        format_utils.convert(s, output_format),
    )


def pack_vrs(
    *vrs: spec.Data,
    mode: Literal['transaction', 'ecdsa'],
    v: spec.Data | None = None,
    r: spec.Data | None = None,
    s: spec.Data | None = None,
) -> str:

    if len(vrs) == 3:
        v, r, s = vrs

    if v is not None and r is not None and s is not None:
        v_bytes = format_utils.convert(v, 'binary', n_bytes=1)
        r_bytes = format_utils.convert(r, 'binary', n_bytes=32)
        s_bytes = format_utils.convert(s, 'binary', n_bytes=32)
    else:
        raise Exception('must specify v, r, and s')

    if mode == 'ecdsa':
        signature = r_bytes + s_bytes + v_bytes
    elif mode == 'transaction':
        delimiter = bytes.fromhex('a0')
        signature = v_bytes + delimiter + r_bytes + delimiter + s_bytes
    else:
        raise Exception('unknown vrs packing mode: ' + str(mode))

    return format_utils.convert(signature, 'prefix_hex')


def unpack_vrs(signature: spec.Signature) -> tuple[int, int, int]:

    if isinstance(signature, tuple):
        v, r, s = signature

    else:
        bytes_signature = format_utils.convert(signature, 'binary')

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
        format_utils.convert(v, 'integer'),
        format_utils.convert(r, 'integer'),
        format_utils.convert(s, 'integer'),
    )


def vrs_to_network_id(*, v: int, r: int, s: int) -> int | None:
    """adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/transactions.py#L93"""
    if r == 0 and s == 0:
        return v
    elif v in (27, 28):
        return None
    else:
        return ((v - 1) // 2) - 17
