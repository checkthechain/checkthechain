from ctc import rpc


async def async_is_contract_address(address, block='latest', provider=None):
    code = await rpc.async_eth_get_code(
        address=address, block_number=block, provider=provider,
    )
    return len(code) > 3


async def async_are_contract_addresses(addresses, block='latest', provider=None):
    codes = await rpc.async_batch_eth_get_code(
        addresses=addresses, block_number=block, provider=provider,
    )
    block = list(codes.keys())[0]
    return {address: len(code) > 3 for address, code in codes[block].items()}

