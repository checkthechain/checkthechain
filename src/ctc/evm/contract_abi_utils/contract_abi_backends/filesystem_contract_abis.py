import json
import os

from ctc import config_utils
from ctc.toolbox import backend_utils


#
# # paths
#

def get_contract_abis_root():
    config = config_utils.get_config()
    return os.path.join(config['evm_root'], 'contract_abis')


def get_contract_abi_dir(contract_address):
    contract_address = contract_address.lower()
    return os.path.join(
        get_contract_abis_root(), 'contract__' + contract_address
    )


def get_contract_abi_filepath(contract_address, name):
    filename = name + '.json'
    return os.path.join(get_contract_abi_dir(contract_address), filename)


#
# # list
#


def list_contract_abi_contracts():
    root = get_contract_abis_root()
    contracts = {}
    for filename in os.listdir(root):
        _, contract_address = filename.split('__')
        contracts[contract_address] = os.path.join(root, filename)
    return contracts


def list_contract_abi_files(contract_address):
    contract_abi_dir = get_contract_abi_dir(contract_address=contract_address)
    paths = []
    if os.path.isdir(contract_abi_dir):
        for filename in sorted(os.listdir(contract_abi_dir)):
            path = os.path.join(contract_abi_dir, filename)
            paths.append(path)
    return paths


def print_contract_abis_summary():
    contract_abi_contracts = list_contract_abi_contracts()
    print('## Contracts with ABI\'s (' + str(len(contract_abi_contracts)) + ')')
    for contract_address, contract_dir in sorted(contract_abi_contracts.items()):
        print(
            '-',
            contract_address,
            '(' + str(len(os.listdir(contract_dir))),
            'files)',
        )


#
# # filesystem
#


def save_contract_abi_to_filesystem(
    contract_abi, contract_address, name=None, overwrite=False
):
    contract_address = contract_address.lower()

    if name is None:
        name = 'contract__' + contract_address
    path = get_contract_abi_filepath(
        contract_address=contract_address,
        name=name,
    )
    if not overwrite and os.path.exists(path):
        raise Exception('path already exists, use overwrite=True')
    os.makedirs(os.path.dirname(path), exist_ok=True)

    print('saving contract_abi to: ' + str(path))
    with open(path, 'w') as f:
        json.dump(contract_abi, f)

    return contract_abi


def get_contract_abi_from_filesystem(contract_address, name=None):
    """concatenate all abi files unless a specific name is given"""
    contract_address = contract_address.lower()

    # gather paths
    if name is None:
        paths = list_contract_abi_files(contract_address=contract_address)
    else:
        path = get_contract_abi_filepath(
            contract_address=contract_address, name=name
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

