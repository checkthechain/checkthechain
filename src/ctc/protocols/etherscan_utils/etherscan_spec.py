from __future__ import annotations

import typing

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


def get_abi_url_template(network: spec.NetworkName) -> str:
    if network not in abi_url_templates:
        raise Exception('block explorer unknown for network=' + str(network))
    else:
        return abi_url_templates[network]
