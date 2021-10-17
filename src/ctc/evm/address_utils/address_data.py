import web3


def is_address_str(some_str):
    return (
        isinstance(some_str, str)
        and some_str.startswith('0x')
        and len(some_str) == 42
    )


def create_hash_preview(
    hash_data,
    show_start=True,
    show_end=True,
    include_0x=True,
    n_chars=6,
    n_chars_start=None,
    n_chars_end=None,
):

    if not include_0x and hash_data[:2] == '0x':
        hash_data = hash_data[2:]

    if n_chars_start is None:
        n_chars_start = n_chars
        if include_0x:
            n_chars_start += 2
    if n_chars_end is None:
        n_chars_end = n_chars

    preview = '...'
    if show_start:
        preview = hash_data[:n_chars_start] + preview
    if show_end:
        preview = preview + hash_data[:-n_chars_end]

    return preview


def get_address_checksum(address):
    return web3.Web3.toChecksumAddress(address)


def create_reverse_address_map(
    address_map, include_lower=True, include_checksum=True
):
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

