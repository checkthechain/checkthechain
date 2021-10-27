"""this module should be deprecated soon in favor of
- raw contract_address <-> contract_abi storage
- raw contract_address <-> contract_name storage
"""
import os
import json
import requests

import toolcache

from ctc import config_utils
from ctc import directory


def get_named_contract_abi_root():
    config = config_utils.get_config()
    return os.path.join(config['evm_root'], 'named_contract_abis')


@toolcache.cache('memory')
def load_named_contract_abi(*, contract_address=None, contract_name=None, project=None):
    if contract_address is not None:
        return load_named_abi_by_address(contract_address)
    elif contract_name is not None:
        return load_abi_by_name(contract_name=contract_name, project=project)
    else:
        raise Exception('not enough information specified')


def load_abi_by_name(contract_name, project=None):

    if contract_name.startswith('[') or contract_name.startswith('{'):
        return json.loads(contract_name)

    else:

        # get abi dir
        abi_dir = get_named_contract_abi_root()
        if project is not None:
            abi_dir = os.path.join(abi_dir, project)

        # read abi file
        path = os.path.join(abi_dir, contract_name + '.json')
        with open(path) as f:
            return json.load(f)


def load_contract_metadata(contract_address, unknown='raise'):

    common_name = None
    if (contract_address in directory.address_to_symbol) and (
        directory.address_to_symbol[contract_address]
        in directory.token_contract_files
    ):
        symbol = directory.address_to_symbol[contract_address]
        contract_name = directory.token_contract_files[symbol]
        project = symbol.lower()
    elif contract_address in directory.contract_address_metadata:
        contract_metadata = directory.contract_address_metadata[
            contract_address
        ]
        if len(contract_metadata) == 2:
            project, contract_name = contract_metadata
        else:
            project, contract_name, common_name = contract_metadata
    elif contract_address in directory.uniswap_v2_pools.values():
        common_name = directory.address_to_symbol[contract_address]
        contract_name = 'UniswapV2Pair'
        project = 'uniswap'
    elif contract_address in directory.uniswap_v3_pools.values():
        common_name = directory.address_to_symbol[contract_address]
        contract_name = 'UniswapV3Pool'
        project = 'uniswap'
    elif contract_address in directory.sushi_pools.values():
        common_name = directory.sushi_address_to_names[contract_address]
        contract_name = 'UniswapV2Pair'
        project = 'sushi'
    elif contract_address in directory.fei_addresses.values():
        contract_name = directory.address_to_fei_name[contract_address]
        contract_name = directory.get_fei_contract_name(contract_name)
        project = 'fei'
    elif contract_address in directory.rari_pool_tokens.values():
        project = 'rari'
        contract_name = 'CErc20Delegator'
        common_name = directory.rari_address_to_names[contract_address]
    else:
        if unknown == 'none':
            return None
        else:
            raise Exception(
                'unknown contract address: ' + str(contract_address)
            )

    if common_name is None:
        common_name = contract_name

    return {
        'common_name': common_name,
        'contract_name': contract_name,
        'project': project,
    }


@toolcache.cache('memory')
def load_named_abi_by_address(contract_address):
    metadata = load_contract_metadata(contract_address=contract_address)
    return load_abi_by_name(
        contract_name=metadata['contract_name'], project=metadata['project']
    )


def fetch_abi(contract_address):
    url_template = 'http://api.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw'
    abi_endpoint = url_template.format(address=contract_address)
    abi = json.loads(requests.get(abi_endpoint).text)
    return abi

