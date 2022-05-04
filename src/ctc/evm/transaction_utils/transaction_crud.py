from __future__ import annotations

import asyncio
import typing

from ctc import rpc
from ctc import spec


async def async_get_transaction(transaction_hash: str) -> spec.Transaction:
    return await rpc.async_eth_get_transaction_by_hash(transaction_hash)


async def async_get_transaction_count(address: spec.Address) -> int:
    return await rpc.async_eth_get_transaction_count(address)


async def async_get_transactions(
    transaction_hashes: typing.Sequence[str],
) -> list[spec.Transaction]:
    coroutines = [
        async_get_transaction(transaction_hash)
        for transaction_hash in transaction_hashes
    ]
    return await asyncio.gather(*coroutines)

