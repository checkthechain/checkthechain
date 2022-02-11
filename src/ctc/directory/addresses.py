from __future__ import annotations

import os
import typing

import ctc.config
from ctc import spec
from ctc.toolbox import store_utils
from ctc.toolbox import search_utils
from . import networks


def get_address_metadata(
    *,
    label: str,
    address: typing.Optional[spec.Address] = None,
    name: typing.Optional[str] = None,
    contract_name: typing.Optional[str] = None,
    block: typing.Optional[spec.BlockNumberReference] = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.AddressMetadata:

    if network is None:
        network = ctc.config.get_default_network()

    if backend == 'Filesystem':

        # load addresses
        addresses = load_filesystem_label_addresses(
            label=label, network=network
        )

        # build query
        query = {
            'address': address,
            'name': name,
            'contract_name': contract_name,
        }
        query = {k: v for k, v in query.items() if v is not None}

        if block is None:
            return search_utils.get_matching_entry(
                sequence=addresses, query=query
            )
        else:

            # find matches
            matches = search_utils.get_matching_entries(
                sequence=addresses, query=query
            )
            if len(matches) == 0:
                raise LookupError('no address found')
            if any(match['first_block'] is None for match in matches):
                raise LookupError('addresses do not specify block range')

            # cast because not None established above
            first_blocks = typing.cast(
                list[tuple[int, int]],
                [(match['first_block'], m) for m, match in enumerate(matches)],
            )

            # sort matches
            first_blocks = sorted(first_blocks)

            if block == 'latest':
                # case: return latest
                return matches[first_blocks[-1][1]]

            elif isinstance(block, int):
                # case: search for latest valid match
                if block < first_blocks[0][0]:
                    raise LookupError('no matching address for specified block')
                for m in range(1, len(matches)):
                    if block < first_blocks[m][0]:
                        return matches[first_blocks[m - 1][1]]
                else:
                    return matches[first_blocks[-1][1]]

            else:
                raise Exception(
                    'unsupported block specification: ' + str(block)
                )

    else:
        raise NotImplementedError('storage backend: ' + str(backend))


def get_address_first_block(
    *,
    label: str,
    address: typing.Optional[spec.Address] = None,
    name: typing.Optional[str] = None,
    contract_name: typing.Optional[str] = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> int:

    metadata = get_address_metadata(
        address=address,
        name=name,
        contract_name=contract_name,
        label=label,
        network=network,
        backend=backend,
    )

    first_block = metadata.get('first_block')
    if first_block is not None:
        return first_block
    else:
        raise Exception('first block not specified for addresss')


def get_address(
    *,
    label: str,
    address: typing.Optional[spec.Address] = None,
    name: typing.Optional[str] = None,
    contract_name: typing.Optional[str] = None,
    block: spec.BlockNumberReference = None,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
) -> spec.Address:

    return get_address_metadata(
        address=address,
        name=name,
        contract_name=contract_name,
        block=block,
        label=label,
        network=network,
        backend=backend,
    )['address']


def load_filesystem_label_addresses(
    label: str,
    network: spec.NetworkReference,
) -> list[spec.AddressMetadata]:
    path = get_filesystem_address_path(label=label, network=network)
    return store_utils.load_file_data(path=path)


def get_filesystem_address_path(
    label: str,
    network: spec.NetworkReference,
    root: typing.Optional[spec.FilesystemRoot] = None,
) -> str:

    if root is None:
        root = 'root'

    if root == 'root':
        data_dir = ctc.config.get_data_dir()
    elif root == 'default':
        data_dir = ctc.config.get_default_data_dir()
    else:
        raise Exception()

    network_name = networks.get_network_name(network=network)
    return os.path.join(data_dir, network_name, 'addresses', label + '.csv')

