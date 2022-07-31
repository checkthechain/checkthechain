from __future__ import annotations

import typing

from ctc import evm
from ctc import spec


url_templates: typing.Mapping[str, str] = {
    'abi': 'https://{api_subdomain}/api?module=contract&action=getabi&address={address}&format=raw',
    'address': 'https://{hostname}/address/{address}',
    'address_erc20_transfers': 'https://{hostname}/tokentxns?a={address}',
    'address_internal_txs': 'https://{hostname}/txsinternal?ps=100&zero=false&a={address}&valid=all&m=advanced',
    'address_holdings': 'https://{hostname}/tokenholdings?a={address}',
    'block': 'https://{hostname}/block/{block}',
    'token': 'https://{hostname}/token/{token_address}',
    'token_holders': 'https://{hostname}/token/{token_address}#balances',
    'transaction': 'https://{hostname}/tx/{transaction_hash}',
    'transaction_logs': 'https://{hostname}/tx/{transaction_hash}#eventlog',
    'transaction_state_changes': 'https://{hostname}/tx/{transaction_hash}#statechange',
}


def get_hostname(network: spec.NetworkReference) -> str:
    block_explorer = evm.get_network_block_explorer(network)
    if block_explorer is None:
        raise Exception('hostname unknown for network: ' + str(network))
    return block_explorer


def get_api_subdomain(network: spec.NetworkReference) -> str:

    non_etherscan_block_explorers = [
        'gnosis',
        'harmony',
        'harmony_testnet',
    ]
    api_dash_subdomains = [
        'ropsten',
        'kovan',
        'rinkeby',
        'goerli',
        'optimism',
        'kovan-optimistic',
        'bnb_testnet',
    ]

    block_explorer = get_hostname(network)
    network_name = evm.get_network_name(network)
    if network_name in non_etherscan_block_explorers:
        raise NotImplementedError(
            'no abi source for network: ' + str(network_name)
        )
    elif network_name in api_dash_subdomains:
        return 'api-' + block_explorer
    else:
        return 'api.' + block_explorer


def create_abi_url(
    address: spec.Address, network: spec.NetworkReference = 'mainnet'
) -> str:
    api_subdomain = get_api_subdomain(network)
    template = url_templates['abi']
    return template.format(api_subdomain=api_subdomain, address=address)


def create_address_url(
    address: spec.Address,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['address']
    return template.format(hostname=hostname, address=address)


def create_address_erc20_transfers_url(
    address: spec.Address,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['address_erc20_transfers']
    return template.format(hostname=hostname, address=address)


def create_address_internal_txs_url(
    address: spec.Address,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['address_internal_txs']
    return template.format(hostname=hostname, address=address)


def create_address_holdings_url(
    address: spec.Address,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['address_holdings']
    return template.format(hostname=hostname, address=address)


def create_block_url(
    block: int,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['block']
    return template.format(hostname=hostname, block=block)


def create_token_url(
    token_address: spec.Address,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['token']
    return template.format(hostname=hostname, token_address=token_address)


def create_token_holders_url(
    token_address: spec.Address,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['token_holders']
    return template.format(hostname=hostname, token_address=token_address)


def create_transaction_url(
    transaction_hash: str,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['transaction']
    return template.format(hostname=hostname, transaction_hash=transaction_hash)


def create_transaction_logs_url(
    transaction_hash: str,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['transaction_logs']
    return template.format(hostname=hostname, transaction_hash=transaction_hash)


def create_transaction_state_changes_url(
    transaction_hash: str,
    network: spec.NetworkReference = 'mainnet',
) -> str:
    hostname = get_hostname(network)
    template = url_templates['transaction_state_changes']
    return template.format(hostname=hostname, transaction_hash=transaction_hash)
