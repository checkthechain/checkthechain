import web3


def is_address_str(some_str):
    return (
        isinstance(some_str, str)
        and some_str.startswith('0x')
        and len(some_str) == 42
    )


def get_address_checksum(address):
    return web3.Web3.toChecksumAddress(address)


def create_reverse_address_map(address_map, include_lower=True, include_checksum=True):
    if not include_lower and not include_checksum:
        raise Exception(
            'must include lower case addresses and/or checksum addresses'
        )

    reverse_map = {}
    for name, address in address_map.items():
        if include_lower:
            reverse_map[address.lower()] = name
        if include_checksum:
            reverse_map[web3.Web3.toChecksumAddress(address)] = name

    return reverse_map

