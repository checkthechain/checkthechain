import os

import pytest
import toolconfig

from ctc import spec
from ctc import directory


@pytest.mark.parametrize(
    'test',
    [
        [1, 'mainnet'],
        ['mainnet', 'mainnet'],
        [3, 'ropsten'],
    ],
)
def test_get_network_name(test):
    network_reference, network_name = test

    actual_network_name = directory.get_network_name(network=network_reference)
    assert actual_network_name == network_name


@pytest.mark.parametrize(
    'test',
    [
        [1, 1],
        ['mainnet', 1],
        ['ropsten', 3],
    ],
)
def test_get_chain_id(test):
    network_reference, network_chain_id = test

    actual_network_chain_id = directory.get_network_chain_id(
        network=network_reference
    )
    assert actual_network_chain_id == network_chain_id


def test_get_network_metadata():
    metadata = directory.get_network_metadata(network=1)
    assert metadata['name'] == 'mainnet'
    assert metadata['chain_id'] == 1
    assert metadata['block_explorer'] == 'etherscan.io'


def test_get_networks():
    networks = directory.get_networks()
    for network_metadata in networks.values():
        toolconfig.conforms_to_spec(
            data=network_metadata, spec=spec.NetworkMetadata
        )


def test_get_networks_file_path():
    path = directory.get_networks_file_path(use_default=True)
    assert os.path.isfile(path)

