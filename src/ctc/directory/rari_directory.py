from ctc import evm


rari_pool_names = {
    'pool_8': 'FeiRari',
}

rari_comptrollers = {
    'pool_8': '0xc54172e34046c1653d1920d40333dd358c7a1af4',
}

rari_pool_tokens = {
    'pool_8__FEI': '0xd8553552f8868c1ef160eedf031cf0bcf9686945',
    'pool_8__TRIBE': '0xfd3300a9a74b3250f1b2abc12b47611171910b07',
    'pool_8__ETH': '0xbb025d470162cc5ea24daf7d4566064ee7f5f111',
    'pool_8__DAI': '0x7e9ce3caa9910cc048590801e64174957ed41d43',
}

rari_address_to_names = evm.create_reverse_address_map(rari_pool_tokens)

