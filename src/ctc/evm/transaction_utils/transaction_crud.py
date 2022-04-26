from ctc import rpc


async def async_get_transaction(transaction_hash):
    return await rpc.async_eth_get_transaction_by_hash(transaction_hash)


async def async_get_transaction_count(address):
    return await rpc.async_eth_get_transaction_count(address)

