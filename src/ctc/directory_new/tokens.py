import os
import typing

import toolcache

import ctc.config
from ctc import spec
from ctc.toolbox import search_utils
from ctc.toolbox import store_utils
from . import networks


_LabelGroup = typing.Union[str, typing.Sequence[str]]

default_token_label = '1inch'


def get_token_metadata(
    *,
    symbol: typing.Optional[spec.TokenSymbol] = None,
    address: typing.Optional[spec.TokenAddress] = None,
    label: typing.Optional[_LabelGroup] = None,
    network: spec.NetworkReference = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.TokenMetadata:

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
            label = default_token_label
        if isinstance(label, str):
            label_list = [label]
        else:
            label_list = label

        # query each label, return the first one that matches
        for query_label in label_list:

            # load label tokens
            tokens_data = load_filesystem_tokens_data(
                network=network,
                label=query_label,
            )

            # return if match found
            try:
                token_data = search_utils.get_matching_entry(
                    tokens_data,
                    **query
                )
                return token_data
            except search_utils.NoMatchFound:
                pass

        else:
            raise LookupError('could not find token metadata')

    else:
        raise Exception('unknown backend: ' + str(backend))


def get_token_address(
    symbol: typing.Optional[spec.TokenSymbol],
    *,
    address: typing.Optional[spec.TokenAddress] = None,
    label: typing.Optional[str] = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.TokenAddress:

    if address is not None:
        return address

    metadata = get_token_metadata(
        symbol=symbol,
        label=label,
        network=network,
        backend=backend,
    )

    return metadata['address']


def get_token_symbol(
    address: typing.Optional[spec.TokenAddress] = None,
    *,
    symbol: typing.Optional[spec.TokenSymbol] = None,
    label: typing.Optional[str] = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.TokenSymbol:

    if symbol is not None:
        return symbol

    metadata = get_token_metadata(
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
def load_filesystem_tokens_data(
    network: spec.NetworkReference,
    label: typing.Optional[str] = None,
) -> list[spec.TokenMetadata]:

    # set default label
    if label is None:
        label = '1inch'

    # build path
    path = get_token_data_path(network=network, label=label)

    # load data
    return store_utils.load_file_data(path)


def get_token_data_path(network: spec.NetworkReference, label: str) -> str:
    network_name = networks.get_network_name(network=network)
    data_dir = ctc.config.get_data_dir()
    filename = label + '.csv'
    return os.path.join(data_dir, network_name, 'tokens', filename)

