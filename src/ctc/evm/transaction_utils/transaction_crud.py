from __future__ import annotations

from ctc import rpc
from ctc import spec


async def async_get_transaction(transaction_hash: str) -> spec.Transaction:
    return await rpc.async_eth_get_transaction_by_hash(transaction_hash)


async def async_get_transaction_count(address: spec.Address) -> int:
    return await rpc.async_eth_get_transaction_count(address)

