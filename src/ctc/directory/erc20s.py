from __future__ import annotations

import os
import typing

import toolcache

import ctc.config
from ctc import spec
from ctc.toolbox import search_utils
from ctc.toolbox import store_utils
from . import networks


_LabelGroup = typing.Union[str, typing.Sequence[str]]

default_erc20_label = '1inch'


def get_erc20_metadata(
    *,
    symbol: typing.Optional[spec.ERC20Symbol] = None,
    address: typing.Optional[spec.ERC20Address] = None,
    label: typing.Optional[_LabelGroup] = None,
    network: spec.NetworkReference = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.ERC20Metadata:

    if network is None:
        network = ctc.config.get_default_network()

    if backend == 'Filesystem':

        # build query
        query = {}
        if symbol is not None:
            query['symbol'] = symbol
        if address is not None:
            query['address'] = address.lower()

        # get label list
        if label is None:
            label = default_erc20_label
        if isinstance(label, str):
            label_list: _LabelGroup = [label]
        else:
            label_list = label

        # query each label, return the first one that matches
        for query_label in label_list:

            # load label erc20
            erc20_data = load_filesystem_erc20_data(
                network=network,
                label=query_label,
            )

            # return if match found
            try:
                return search_utils.get_matching_entry(
                    erc20_data,
                    query=query,
                )
            except search_utils.NoMatchFound:
                pass

        else:
            raise LookupError('could not find erc20 metadata')

    else:
        raise Exception('unknown backend: ' + str(backend))


def get_erc20_address(
    symbol: typing.Optional[spec.ERC20Symbol],
    *,
    address: typing.Optional[spec.ERC20Address] = None,
    label: typing.Optional[str] = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.ERC20Address:

    if address is not None:
        return address

    metadata = get_erc20_metadata(
        symbol=symbol,
        label=label,
        network=network,
        backend=backend,
    )

    return metadata['address']


def has_erc20_metadata(
    address: typing.Optional[spec.ERC20Address] = None,
    symbol: typing.Optional[spec.ERC20Symbol] = None,
    **kwargs,
) -> bool:

    try:
        get_erc20_metadata(address=address, symbol=symbol, **kwargs)
        return True
    except LookupError:
        return False


def get_erc20_symbol(
    address: typing.Optional[spec.ERC20Address] = None,
    *,
    symbol: typing.Optional[spec.ERC20Symbol] = None,
    label: typing.Optional[str] = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.ERC20Symbol:

    if symbol is not None:
        return symbol

    metadata = get_erc20_metadata(
        label=label,
        address=address,
        backend=backend,
        network=network,
    )

    return metadata['symbol']


#
# # backend-specific
#


@toolcache.cache(cachetype='memory')
def load_filesystem_erc20_data(
    network: spec.NetworkReference,
    label: typing.Optional[str] = None,
) -> list[spec.ERC20Metadata]:

    # set default label
    if label is None:
        label = '1inch'

    # build path
    path = get_erc20_data_path(network=network, label=label)

    # load data
    return store_utils.load_file_data(path)


def get_erc20_data_path(network: spec.NetworkReference, label: str) -> str:
    network_name = networks.get_network_name(network=network)
    data_dir = ctc.config.get_data_dir()
    filename = label + '.csv'
    return os.path.join(data_dir, network_name, 'erc20s', filename)

