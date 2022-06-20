from __future__ import annotations

import os
import typing

from ctc import config
from ctc import evm
from ctc import spec


abi_url_templates: typing.Mapping[str, str] = {
    'mainnet': 'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'ropsten': 'https://api-ropsten.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'kovan': 'https://api-kovan.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'rinkeby': 'https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'goerli': 'https://api-goerli.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'arbitrum': 'https://api.arbiscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'avalanche': 'https://api.snowtrace.io/api?module=contract&action=getabi&address={address}&format=raw',
    'bsc': 'http://api.bscscan.com/api?module=contract&action=getabi&address={address}&format=raw',
    'optimism': 'https://api-optimistic.etherscan.io/api?module=contract&action=getabi&address={address}&format=raw',
    'polygon': 'https://api.polygonscan.com/api?module=contract&action=getabi&address={address}&format=raw',
}


def get_abi_url_template(network: spec.NetworkReference) -> str:

    if network is None:
        network = config.get_default_network()
    network = evm.get_network_name(network, require=True)

    if network not in abi_url_templates:
        raise Exception('block explorer unknown for network=' + str(network))

    template = abi_url_templates[network]

    key = get_etherscan_key(network=network)
    if key is not None:
        template = template + '&apikey=' + str(key)

    return template


def get_etherscan_key(network: spec.NetworkName) -> str | None:
    if network == 'mainnet':
        key = os.environ.get('ETHERSCAN_API_KEY')
        if key == '':
            return None
        else:
            return key
    else:
        return None
