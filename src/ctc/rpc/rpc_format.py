import re
import typing

from ctc.evm import binary_utils
from ctc import spec


T = typing.TypeVar('T')


def encode_block_number(block: typing.Union[int, str]) -> str:
    if isinstance(block, str) and block in ['latest', 'earliest', 'pending']:
        return block
    else:
        return binary_utils.convert_binary_format(block, 'prefix_hex')


def decode_response(
    response: dict[str, typing.Union[int, str]],
    quantities: typing.Optional[list[str]] = None,
) -> dict:
    if quantities is None:
        quantities = []
    decoded = {}
    for key, value in response.items():
        if key in quantities:
            value = binary_utils.convert_binary_format(value, 'integer')
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

