from __future__ import annotations

import typing

from ctc import spec


def decode_types(data: bytes, types: spec.ABIDatatypeStr) -> typing.Any:
    # TODO: allow for any input format, allow specifying any output format
    import eth_abi_lite

    return eth_abi_lite.decode_single(types, data)


def encode_types(data: typing.Any, types: spec.ABIDatatypeStr) -> bytes:
    # TODO: allow for any input format, allow specifying any output format
    import eth_abi_lite

    return eth_abi_lite.encode_single(types, data)


def abi_encode_packed(data: typing.Any, types: spec.ABIDatatypeStr) -> bytes:
    from eth_abi_lite import packed

    return packed.encode_single_packed(types, data)
