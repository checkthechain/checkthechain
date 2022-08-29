from __future__ import annotations

from ctc import spec
from .. import formats
from . import key_crud
from . import secp256k1_utils
from . import vrs_utils


def get_signature_network_id(signature: spec.Data) -> int | None:
    v, r, s = vrs_utils.unpack_vrs(signature)
    return vrs_utils.vrs_to_network_id(v=v, r=r, s=s)


def get_signer_public_key(
    message_hash: spec.Data,
    *,
    signature: spec.Data | None = None,
    v: spec.Data | None = None,
    r: spec.Data | None = None,
    s: spec.Data | None = None,
) -> str:
    """

    must either provide signature or (v, r, s)

    adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/utils.py#L87
    """

    # ger vrs
    if isinstance(signature, tuple):
        v, r, s = signature
    if v is None or r is None or s is None:
        if signature is None:
            raise Exception('must provide more arguments')
        v, r, s = vrs_utils.unpack_vrs(signature)

    v = formats.convert(v, 'integer')
    r = formats.convert(r, 'integer')
    s = formats.convert(s, 'integer')

    if v >= 37:
        network_id = vrs_utils.vrs_to_network_id(v=v, r=r, s=s)
        if network_id is None:
            raise Exception('could not parse valid network_id')
        v = v - network_id * 2 - 8

    # get signer
    message_hash = formats.convert(message_hash, 'binary')
    x, y = secp256k1_utils.ecdsa_raw_recover(message_hash, (v, r, s))
    signer = x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')

    return formats.convert(signer, 'prefix_hex')


def get_signer_address(
    message_hash: spec.Data,
    signature: spec.Data | None = None,
    *,
    v: spec.Data | None = None,
    r: spec.Data | None = None,
    s: spec.Data | None = None,
) -> spec.Address:
    public_key = get_signer_public_key(
        message_hash=message_hash,
        signature=signature,
        v=v,
        r=r,
        s=s,
    )
    return key_crud.public_key_to_address(public_key)
