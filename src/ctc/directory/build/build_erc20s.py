"""
ERC20 lists obtained from https://erc20lists.org/
"""

import typing
from typing_extensions import TypedDict

from ctc import directory
from ctc import spec
from ctc.toolbox import store_utils


class ERC20ListPayload(TypedDict):
    name: str
    timestamp: str
    version: 'ERC20ListVersion'
    keywords: list[str]
    erc20s: list['ERC20ListToken']


class ERC20ListVersion(TypedDict):
    major: int
    minor: int
    patch: int


class ERC20ListToken(TypedDict):
    address: spec.Address
    chainId: int
    name: str
    symbol: str
    decimals: int
    logoURI: str


def import_erc20_list_payload(
    erc20_list_payload: ERC20ListPayload,
    network: spec.NetworkReference,
    label: typing.Optional[str],
    backend: spec.StorageBackend,
    overwrite: bool = False,
) -> None:

    if backend != 'Filesystem':
        raise NotImplementedError('backend ' + str(backend))

    # check that all erc20s are from specified network
    chain_id = directory.get_network_chain_id(network=network)
    for erc20 in erc20_list_payload['erc20s']:
        if erc20['chainId'] != chain_id:
            raise Exception('erc20s from other network in list')

    # get output path
    if label is None:
        label = erc20_list_payload['name']
    output_path = directory.get_erc20_data_path(network=network, label=label)

    # convert data
    data: list[spec.ERC20Metadata] = [
        {
            'name': erc20['name'],
            'address': erc20['address'].lower(),
            'symbol': erc20['symbol'],
            'decimals': erc20['decimals'],
        }
        for erc20 in erc20_list_payload['erc20s']
    ]

    # write data
    store_utils.write_file_data(
        path=output_path, data=data, overwrite=overwrite,
    )

    print('imported data to path', output_path)

