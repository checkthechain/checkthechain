from ctc import evm

saddle_pools = {
    'd4': '0xc69ddcd4dfef25d8a793241834d4cc4b3668ead6',
}

saddle_address_to_names = evm.create_reverse_address_map(saddle_pools)

