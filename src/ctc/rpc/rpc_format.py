from __future__ import annotations

import re
import typing

from ctc import evm


if typing.TYPE_CHECKING:
    T = typing.TypeVar('T')


def decode_response(
    response: dict[str, typing.Union[int, str]],
    quantities: typing.Optional[list[str]] = None,
) -> dict[str, typing.Any]:
    if quantities is None:
        quantities = []
    decoded = {}
    for key, value in response.items():
        if key in quantities:
            value = evm.binary_convert(value, 'integer')
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
