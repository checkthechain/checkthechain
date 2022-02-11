from __future__ import annotations

import re
import typing

from ctc import binary
from ctc import spec


T = typing.TypeVar('T')


def encode_block_number(block: spec.BlockSpec) -> str:

    if isinstance(block, str) and block in ['latest', 'earliest', 'pending']:
        return block
    else:
        # python3.7 compatibliity
        supports_int = hasattr(block, '__int__')
        # supports_int = isinstance(block, typing.SupportsInt)

        if supports_int:
            block = int(block)
        return binary.convert(block, 'prefix_hex')


def decode_response(
    response: dict[str, typing.Union[int, str]],
    quantities: typing.Optional[list[str]] = None,
) -> dict:
    if quantities is None:
        quantities = []
    decoded = {}
    for key, value in response.items():
        if key in quantities:
            value = binary.convert(value, 'integer')
        decoded[key] = value
    return decoded


def keys_to_snake_case(map: dict[str, T]) -> dict[str, T]:
    """

    not for general usage beyond the keys that appear in the EVM rpc spec

    adapted from https://stackoverflow.com/a/1176023
    """
    return {camel_case_to_snake_case(key): value for key, value in map.items()}


def camel_case_to_snake_case(text: str) -> str:
    """

    not for general usage beyond the keys that appear in the EVM rpc spec

    adapted from https://stackoverflow.com/a/1176023
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

