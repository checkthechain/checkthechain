from __future__ import annotations

import typing

from ctc import spec
from .. import binary_utils


def abi_decode(
    data: spec.GenericBinaryData,
    types: spec.ABIDatatypeStr | typing.Sequence[spec.ABIDatatypeStr],
    *,
    convert_invalid_str_to_none: bool = False,
    convert_invalid_str_to: str | None = None,
) -> typing.Any:
    """decode ABI-encoded data, similar to solidity's abi.decode()"""

    import eth_abi_lite

    data = binary_utils.to_binary(data)

    # TODO: more general left padding for irregular sized data
    if data == b'':
        data = b'\x00' * 32

    # hardcode some conversions for speed
    if types == 'address':
        return '0x' + data[-20:].hex()
    elif types in ['uint256']:
        return int.from_bytes(data, 'big', signed=False)
    # elif types == '(uint256)':
    #     return (int.from_bytes(data, 'big', signed=False),)

    # decode data
    if isinstance(types, str):
        try:
            return eth_abi_lite.decode_single(types, data)
        except eth_abi_lite.exceptions.DecodingError as e:
            # handle improperly encoded data
            if types == 'string':
                if convert_invalid_str_to_none:
                    return None
                elif convert_invalid_str_to is not None:
                    return convert_invalid_str_to
            raise e
    else:
        if len(data) < 64:
            data = b'\x00' * (64 - len(data)) + data
        return eth_abi_lite.decode_abi(types, data)


def abi_encode(
    data: typing.Any,
    types: spec.ABIDatatypeStr | typing.Sequence[spec.ABIDatatypeStr],
) -> bytes:
    """encode data in ABI format, similar to solidity's abi.encode()"""

    import eth_abi_lite

    if isinstance(types, str):
        return eth_abi_lite.encode_single(types, data)
    else:
        return eth_abi_lite.encode_abi(types, data)


def abi_encode_packed(
    data: typing.Any,
    types: spec.ABIDatatypeStr | typing.Sequence[spec.ABIDatatypeStr],
) -> bytes:
    """encode data in ABI format, similar to solidity's abi.encode_packed()"""

    from eth_abi_lite import packed

    if isinstance(types, str):
        return packed.encode_single_packed(types, data)
    else:
        return packed.encode_abi_packed(types, data)
