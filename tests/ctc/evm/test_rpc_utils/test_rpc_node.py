from ctc.evm import binary_utils
from ctc.evm import rpc_utils


def test_web3_client_version():
    result = rpc_utils.web3_client_version()
    assert len(result) > 0


def test_web3_sha():
    data = '0x1234'
    result = rpc_utils.web3_sha3(data)
    keccak = binary_utils.keccak(data, output_format='prefix_hex')
    assert keccak == result


def test_net_version():
    result = rpc_utils.net_version()
    assert len(result) > 0


def test_net_listening():
    listening = rpc_utils.net_listening()
    assert listening is not None


def test_eth_protocol_version():
    version = rpc_utils.eth_protocol_version()
    assert version is not None


def test_eth_syncing():
    syncing = rpc_utils.eth_syncing()
    assert syncing is not None

