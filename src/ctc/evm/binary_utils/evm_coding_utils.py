# replace eth_abi with eth_abi_lite

def decode_evm_data(types, data):
    import eth_abi

    return eth_abi.decode_single(types, data)


def encode_evm_data(types, data):
    import eth_abi

    return eth_abi.encode_single(types, data)

