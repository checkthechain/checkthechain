from __future__ import annotations

import typing

from ctc import spec


def decode_types(
    data: bytes,
    types: spec.ABIDatatypeStr | typing.Sequence[spec.ABIDatatypeStr],
) -> typing.Any:
    # TODO: allow for any input format, allow specifying any output format
    import eth_abi_lite

    if isinstance(types, str):
        return eth_abi_lite.decode_single(types, data)
    else:
        return eth_abi_lite.decode_abi(types, data)


def encode_types(
    data: typing.Any,
    types: spec.ABIDatatypeStr | typing.Sequence[spec.ABIDatatypeStr],
) -> bytes:
    # TODO: allow for any input format, allow specifying any output format
    import eth_abi_lite

    if isinstance(types, str):
        return eth_abi_lite.encode_single(types, data)
    else:
        return eth_abi_lite.encode_abi(types, data)


def abi_encode_packed(
    data: typing.Any,
    types: spec.ABIDatatypeStr | typing.Sequence[spec.ABIDatatypeStr],
) -> bytes:
    from eth_abi_lite import packed

    if isinstance(types, str):
        return packed.encode_single_packed(types, data)
    else:
        return packed.encode_abi_packed(types, data)
