"""
Token lists obtained from https://tokenlists.org/
"""

import os
import typing

import ctc.config
from ctc import directory_new as directory
from ctc import spec
from ctc.toolbox import store_utils


class TokenListPayload(typing.TypedDict):
    name: str
    timestamp: str
    version: 'TokenListVersion'
    keywords: list[str]
    tokens: list['TokenListToken']


class TokenListVersion(typing.TypedDict):
    major: int
    minor: int
    patch: int


class TokenListToken(typing.TypedDict):
    address: spec.Address
    chainId: int
    name: str
    symbol: str
    decimals: int
    logoURI: str


def import_token_list_payload(
    token_list_payload: TokenListPayload,
    network: spec.NetworkReference,
    label: typing.Optional[str],
    backend: spec.StorageBackend,
    overwrite: bool = False,
) -> None:

    if backend != 'Filesystem':
        raise NotImplementedError('backend ' + str(backend))

    # check that all tokens are from specified network
    chain_id = directory.get_network_chain_id(network=network)
    for token in token_list_payload['tokens']:
        if token['chainId'] != chain_id:
            raise Exception('tokens from other network in list')

    # get output path
    if label is None:
        label = token_list_payload['name']
    output_path = directory.get_token_data_path(network=network, label=label)

    # convert data
    data: list[spec.TokenMetadata] = [
        {
            'name': token['name'],
            'address': token['address'].lower(),
            'symbol': token['symbol'],
            'decimals': token['decimals'],
        }
        for token in token_list_payload['tokens']
    ]

    # write data
    store_utils.write_file_data(
        path=output_path, data=data, overwrite=overwrite,
    )

    print('imported data to path', output_path)

