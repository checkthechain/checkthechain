from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec


async def async_get_transaction(transaction_hash: str) -> spec.Transaction:
    return await rpc.async_eth_get_transaction_by_hash(transaction_hash)  # type: ignore


async def async_get_transaction_count(address: spec.Address) -> int:
    result = await rpc.async_eth_get_transaction_count(address)
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_transactions(
    transaction_hashes: typing.Sequence[str],
) -> list[spec.Transaction]:
    import asyncio

    coroutines = [
        async_get_transaction(transaction_hash)
        for transaction_hash in transaction_hashes
    ]
    return await asyncio.gather(*coroutines)
