import json
import os

from fei import config_utils
from fei.data import directory
from fei.data import web3_utils


# should probably deprecate this code for more general functions

def get_fei_abi(contract_name):

    # get abi dir
    config = config_utils.get_config()
    fei_abi_dir = config['fei_abi_dir']
    if fei_abi_dir is None:
        raise Exception('must set fei_abi_dir in config')

    # load file
    path = os.path.join(fei_abi_dir, contract_name + '.json')
    with open(path, 'r') as f:
        return json.load(f)


def contract_call(contract, function, **kwargs):
    if contract in directory.fei_addresses:
        contract_name = contract
        contract_address = directory.fei_addresses[contract]
    else:
        contract_address = contract
        contract_name = directory.address_to_fei_name[contract]

    return web3_utils.contract_call(
        contract=contract_address,
        abi=get_fei_abi(contract_name),
        function=function,
        **kwargs
    )
