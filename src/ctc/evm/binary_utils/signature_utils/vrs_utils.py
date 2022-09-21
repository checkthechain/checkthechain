from __future__ import annotations

import typing

from ctc import spec
from .. import format_utils

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


def pack_signature_vrs(
    *vrs: spec.Data,
    mode: Literal['transaction', 'ecdsa'],
    v: spec.Data | None = None,
    r: spec.Data | None = None,
    s: spec.Data | None = None,
) -> str:
    """convert signature to singleton hdex data representation"""

    if len(vrs) == 3:
        v, r, s = vrs

    if v is not None and r is not None and s is not None:
        v_bytes = format_utils.binary_convert(v, 'binary', n_bytes=1)
        r_bytes = format_utils.binary_convert(r, 'binary', n_bytes=32)
        s_bytes = format_utils.binary_convert(s, 'binary', n_bytes=32)
    else:
        raise Exception('must specify v, r, and s')

    if mode == 'ecdsa':
        signature = r_bytes + s_bytes + v_bytes
    elif mode == 'transaction':
        delimiter = bytes.fromhex('a0')
        signature = v_bytes + delimiter + r_bytes + delimiter + s_bytes
    else:
        raise Exception('unknown vrs packing mode: ' + str(mode))

    return format_utils.binary_convert(signature, 'prefix_hex')


def unpack_signature_vrs(signature: spec.Signature) -> tuple[int, int, int]:
    """convert signature to triplet VRS representation"""

    if isinstance(signature, tuple):
        v, r, s = signature

    else:
        bytes_signature = format_utils.binary_convert(signature, 'binary')

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
        format_utils.binary_convert(v, 'integer'),
        format_utils.binary_convert(r, 'integer'),
        format_utils.binary_convert(s, 'integer'),
    )
