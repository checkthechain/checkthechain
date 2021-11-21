from ctc.evm import rpc_utils


def is_contract_address(address, block='latest', provider=None):
    code = rpc_utils.eth_get_code(
        address=address, block_number=block, provider=provider,
    )
    return len(code) > 3


def are_contract_addresses(addresses, block='latest', provider=None):
    codes = rpc_utils.batch_eth_get_code(
        addresses=addresses, block_number=block, provider=provider,
    )
    block = list(codes.keys())[0]
    return {address: len(code) > 3 for address, code in codes[block].items()}

