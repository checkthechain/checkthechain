import pytest

from ctc import evm
from ctc import rpc


@pytest.mark.asyncio
async def test_web3_client_version():
    result = await rpc.async_web3_client_version()
    assert len(result) > 0


@pytest.mark.asyncio
async def test_web3_sha():
    data = '0x1234'
    result = await rpc.async_web3_sha3(data)
    keccak = evm.keccak(data, output_format='prefix_hex')
    assert keccak == result


@pytest.mark.asyncio
async def test_net_version():
    result = await rpc.async_net_version()
    assert len(result) > 0


@pytest.mark.asyncio
async def test_net_listening():
    listening = await rpc.async_net_listening()
    assert listening is not None


@pytest.mark.asyncio
async def test_eth_protocol_version():
    version = await rpc.async_eth_protocol_version()
    assert version is not None


@pytest.mark.asyncio
async def test_eth_syncing():
    syncing = await rpc.async_eth_syncing()
    assert syncing is not None


@pytest.mark.asyncio
async def test_eth_chain_id():
    chain_id = await rpc.async_eth_chain_id()
    assert isinstance(chain_id, int)
