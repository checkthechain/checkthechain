from ctc.evm import rpc_utils


def test_eth_block_number():
    result = rpc_utils.eth_block_number()
    assert isinstance(result, int)


def test_eth_get_block_by_hash():
    block_hash = (
        '0x767c2bfb3bdee3f78676c1285cd757bcd5d8c272cef2eb30d9733800a78c0b6d'
    )
    block = rpc_utils.eth_get_block_by_hash(block_hash)
    assert block['number'] == 12345


def test_eth_get_block_by_number():
    block = rpc_utils.eth_get_block_by_number(12345)
    assert (
        block['hash']
        == '0x767c2bfb3bdee3f78676c1285cd757bcd5d8c272cef2eb30d9733800a78c0b6d'
    )


def test_eth_get_uncle_count_by_block_hash():
    assert 2 == rpc_utils.eth_get_uncle_count_by_block_hash(
        '0x461336bad4949d91e253631a8f5df8412d258b59da9715ff638922f3c67353f8'
    )


def test_eth_get_uncle_count_by_block_number():
    assert 2 == rpc_utils.eth_get_uncle_count_by_block_number(222)


def test_eth_get_uncle_by_block_hash_and_index():
    block = rpc_utils.eth_get_uncle_by_block_hash_and_index(
        '0x461336bad4949d91e253631a8f5df8412d258b59da9715ff638922f3c67353f8', 1
    )
    assert (
        block['hash']
        == '0x4cf24f3784d19179965ad4f8396fce0f2bf2466d1e25c197021c0969b686f236'
    )


def test_eth_get_uncle_by_block_number_and_index():
    block = rpc_utils.eth_get_uncle_by_block_number_and_index(222, 1)
    assert (
        block['hash']
        == '0x4cf24f3784d19179965ad4f8396fce0f2bf2466d1e25c197021c0969b686f236'
    )

