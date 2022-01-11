import typing

import ctc.config
from ctc import directory
from ctc import spec
from ctc.toolbox import store_utils


_RawAddressData = typing.Union[spec.Address, spec.AddressMetadata]


def import_addresses(
    addresses: dict[str, _RawAddressData],
    label: str,
    overwrite: bool = False,
    network: typing.Optional[spec.NetworkReference] = None,
    backend: spec.StorageBackend = 'Filesystem',
    verbose: bool = True,
    root: typing.Optional[spec.FilesystemRoot] = None,
) -> None:

    if backend != 'Filesystem':
        raise NotImplementedError('storage backend: ' + str(backend))

    if network is None:
        network = ctc.config.get_default_network()

    # process data
    data = []
    for name, address in addresses.items():
        if isinstance(address, str):
            datum: spec.AddressMetadata = {'name': name, 'address': address.lower()}
        elif isinstance(address, dict):
            datum = {
                'name': address['name'],
                'address': address['address'],
            }

            for key, value in address.items():
                if key in ['name', 'address']:
                    pass
                elif key == 'first_block':
                    datum['first_block'] = typing.cast(typing.Optional[int], value)
                elif key == 'contract_name':
                    datum['contract_name'] = typing.cast(typing.Optional[str], value)
                elif key == 'label':
                    assert value == label
                else:
                    raise Exception('unknown key: ' + str(key))
        else:
            raise Exception('unknown address format: ' + str(type(address)))
        data.append(datum)

    # write to disk
    path = directory.get_filesystem_address_path(
        label=label, network=network, root=root
    )
    store_utils.write_file_data(data=data, path=path, overwrite=overwrite)

    # print summary
    if verbose:
        print('wrote', len(addresses), 'addresses to path: ' + str(path))

