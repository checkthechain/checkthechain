from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec
from . import safe_spec


async def async_get_safe_owners(
    address: spec.Address,
    *,
    block: spec.BlockReference | None = None,
) -> typing.Sequence[spec.Address]:
    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=safe_spec.function_abis['getOwners'],
        block_number=block,
    )
    if not isinstance(result, (tuple, list)) or not all(
        isinstance(item, str) for item in result
    ):
        raise Exception('invalid rpc result')
    return result


async def async_get_safe_threshold(
    address: spec.Address,
    *,
    block: spec.BlockReference | None = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=safe_spec.function_abis['getThreshold'],
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_safe_nonce(
    address: spec.Address,
    *,
    block: spec.BlockReference | None = None,
) -> int:
    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=safe_spec.function_abis['nonce'],
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result
