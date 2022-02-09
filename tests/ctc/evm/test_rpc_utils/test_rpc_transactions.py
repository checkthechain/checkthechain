import pytest

from ctc import rpc


@pytest.mark.asyncio
async def test_eth_get_transaction_count():
    result = await rpc.async_eth_get_transaction_count(
        '0x94b0a3d511b6ecdb17ebf877278ab030acb0a878'
    )
    assert result == 1


@pytest.mark.asyncio
async def test_eth_get_transaction_by_block_hash_and_index():
    result = await rpc.async_eth_get_transaction_by_block_hash_and_index(
        block_hash='0xb2a8b39935a5eb4b7c9b0117bca06c8d2c0629e0937d20e62c44aace6f05bda3',
        transaction_index=88,
    )
    assert (
        result['block_hash']
        == '0xb2a8b39935a5eb4b7c9b0117bca06c8d2c0629e0937d20e62c44aace6f05bda3'
    )


@pytest.mark.asyncio
async def test_eth_get_transaction_by_block_number_and_index():
    result = await rpc.async_eth_get_transaction_by_block_number_and_index(
        block_number=12345678,
        transaction_index=88,
    )
    assert (
        result['block_hash']
        == '0xb2a8b39935a5eb4b7c9b0117bca06c8d2c0629e0937d20e62c44aace6f05bda3'
    )


@pytest.mark.asyncio
async def test_eth_get_transaction_by_hash():
    result = await rpc.async_eth_get_transaction_by_hash(
        transaction_hash='0xd764f7b1bfc34acfa052453ee1baf2d016d0c8c4d963a73db5e30780a6f92e7b'
    )
    assert (
        result['block_hash']
        == '0xb2a8b39935a5eb4b7c9b0117bca06c8d2c0629e0937d20e62c44aace6f05bda3'
    )


@pytest.mark.asyncio
async def test_eth_get_transaction_receipt():
    result = await rpc.async_eth_get_transaction_receipt(
        '0xd764f7b1bfc34acfa052453ee1baf2d016d0c8c4d963a73db5e30780a6f92e7b'
    )
    assert (
        result['block_hash']
        == '0xb2a8b39935a5eb4b7c9b0117bca06c8d2c0629e0937d20e62c44aace6f05bda3'
    )


@pytest.mark.asyncio
async def test_get_block_transaction_count_by_hash():
    result = await rpc.async_eth_get_block_transaction_count_by_hash(
        block_hash='0xb2a8b39935a5eb4b7c9b0117bca06c8d2c0629e0937d20e62c44aace6f05bda3'
    )
    assert result == 174


@pytest.mark.asyncio
async def test_eth_get_block_transaction_count_by_number():
    result = await rpc.async_eth_get_block_transaction_count_by_number(
        block_number=12345678
    )
    assert result == 174

