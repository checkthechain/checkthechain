from __future__ import annotations

from ctc import spec
from .. import format_utils
from . import key_utils
from . import secp256k1_utils
from . import vrs_utils


def verify_signature(
    signature: spec.Signature,
    *,
    message_hash: spec.Data,
    public_key: spec.Data | None = None,
    address: spec.Data | None = None,
) -> bool:
    """verify that signature was signed using given public key"""

    # recover public key from signature
    recovered_public_key = recover_signer_public_key(
        message_hash=message_hash,
        signature=signature,
    )

    # verify a match against provided public_key and/or address
    if public_key is None and address is None:
        raise Exception('must provider public_key or address to verify')
    if public_key is not None and public_key != recovered_public_key:
        return False
    if address is not None:
        recovered_address = key_utils.public_key_to_address(
            recovered_public_key
        )
        if recovered_address != address:
            return False

    return True


def get_signature_network_id(signature: spec.Signature) -> int | None:
    """extract network id from given signature

    adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/transactions.py#L93
    """

    v, r, s = vrs_utils.unpack_signature_vrs(signature)
    if r == 0 and s == 0:
        return v
    elif v in (27, 28):
        return None
    else:
        return ((v - 1) // 2) - 17


def recover_signer_public_key(
    *,
    message_hash: spec.Data,
    signature: spec.Signature,
) -> str:
    """recover signer public key from signature

    adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/utils.py#L87
    """

    # ger vrs
    v, r, s = vrs_utils.unpack_signature_vrs(signature)
    v = format_utils.binary_convert(v, 'integer')
    r = format_utils.binary_convert(r, 'integer')
    s = format_utils.binary_convert(s, 'integer')

    if v >= 37:
        network_id = get_signature_network_id(signature)
        if network_id is None:
            raise Exception('could not parse valid network_id')
        v = v - network_id * 2 - 8

    # get signer
    message_hash = format_utils.binary_convert(message_hash, 'binary')
    x, y = secp256k1_utils.ecdsa_raw_recover(message_hash, (v, r, s))
    signer = x.to_bytes(32, byteorder='big') + y.to_bytes(32, byteorder='big')

    return format_utils.binary_convert(signer, 'prefix_hex')


def recover_signer_address(
    *,
    message_hash: spec.Data,
    signature: spec.Signature,
) -> spec.Address:
    """recover signer public address from signature"""

    public_key = recover_signer_public_key(
        message_hash=message_hash,
        signature=signature,
    )
    return key_utils.public_key_to_address(public_key)
