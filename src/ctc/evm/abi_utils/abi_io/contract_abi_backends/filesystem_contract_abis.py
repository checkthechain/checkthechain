import json
import os
import typing

from ctc import config
from ctc import directory
from ctc import spec
from ctc.toolbox import backend_utils


#
# # paths
#


def get_contract_abis_root(
    network: typing.Optional[spec.NetworkReference] = None,
):
    network_name = directory.get_network_name(network)
    return os.path.join(config.get_data_dir(), network_name, 'contract_abis')


def get_contract_abi_dir(
    contract_address: spec.Address,
    network: typing.Optional[spec.NetworkReference] = None,
):
    contract_address = contract_address.lower()
    return os.path.join(
        get_contract_abis_root(network=network), 'contract__' + contract_address
    )


def get_contract_abi_filepath(
    contract_address,
    name,
    network: typing.Optional[spec.NetworkReference] = None,
):
    filename = name + '.json'
    return os.path.join(
        get_contract_abi_dir(contract_address, network=network), filename
    )


#
# # list
#


def list_contract_abi_contracts(network):
    root = get_contract_abis_root(network=network)
    contracts = {}
    for filename in os.listdir(root):
        _, contract_address = filename.split('__')
        contracts[contract_address] = os.path.join(root, filename)
    return contracts


def list_contract_abi_files(
    contract_address,
    network: typing.Optional[spec.NetworkReference] = None,
):
    contract_abi_dir = get_contract_abi_dir(
        contract_address=contract_address, network=network
    )
    paths = []
    if os.path.isdir(contract_abi_dir):
        for filename in sorted(os.listdir(contract_abi_dir)):
            path = os.path.join(contract_abi_dir, filename)
            paths.append(path)
    return paths


def print_contract_abis_summary(
    network: typing.Optional[spec.NetworkReference] = None,
):
    contract_abi_contracts = list_contract_abi_contracts(network=network)
    print('## Contracts with ABI\'s (' + str(len(contract_abi_contracts)) + ')')
    for contract_address, contract_dir in sorted(
        contract_abi_contracts.items()
    ):
        print(
            '-',
            contract_address,
            '(' + str(len(os.listdir(contract_dir))),
            'files)',
        )


#
# # filesystem
#


async def async_save_contract_abi_to_filesystem(
    contract_abi,
    contract_address,
    name=None,
    overwrite=False,
    network: typing.Optional[spec.NetworkReference] = None,
):
    contract_address = contract_address.lower()

    if name is None:
        name = 'contract__' + contract_address
    path = get_contract_abi_filepath(
        contract_address=contract_address,
        name=name,
        network=network,
    )
    if not overwrite and os.path.exists(path):
        raise Exception('path already exists, use overwrite=True')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    print('saving contract_abi to: ' + str(path))
    with open(path, 'w') as f:
        json.dump(contract_abi, f)

    return contract_abi


async def async_save_proxy_contract_abi_to_filesystem(
    contract_address,
    proxy_implementation,
    name='proxy_implementation',
    network: typing.Optional[spec.NetworkReference] = None,
):
    from ctc import evm

    proxy_abi = await evm.async_get_contract_abi(
        contract_address=proxy_implementation,
        network=network,
    )
    await async_save_contract_abi_to_filesystem(
        contract_abi=proxy_abi,
        contract_address=contract_address,
        name=name,
        network=network,
    )


async def async_get_contract_abi_from_filesystem(
    contract_address,
    name=None,
    network: typing.Optional[spec.NetworkReference] = None,
):
    """concatenate all abi files unless a specific name is given"""
    contract_address = contract_address.lower()

    # gather paths
    if name is None:
        paths = list_contract_abi_files(
            contract_address=contract_address,
            network=network,
        )
    else:
        path = get_contract_abi_filepath(
            contract_address=contract_address,
            name=name,
            network=network,
        )
        paths = [path]

    if len(paths) == 0:
        raise backend_utils.DataNotFound(
            'no files found for contract: ' + str(contract_address)
        )
    if len(paths) == 1 and not os.path.isfile(paths[0]):
        raise backend_utils.DataNotFound(
            'file does not exist: ' + str(paths[0])
        )

    # load files
    contract_abi = []
    for path in paths:
        with open(path, 'r') as f:
            contract_abi += json.load(f)

    return contract_abi

