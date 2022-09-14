from __future__ import annotations

import typing

import toolstr

from ctc import spec
from ctc import cli
from . import yearn_spec


def get_yearn_addresses(
    network: spec.NetworkReference,
) -> typing.Mapping[str, spec.Address]:

    if network not in ('mainnet', 1):
        raise NotImplementedError('non-mainnet address')

    mainnnet_addresses = {
        'Oracle': '0x83d95e0d5f402511db06817aff3f9ea88224b030',
        'ManagementList': '0xf64e58ee8c7badc741a7ea98fb65488084385674',
        #
        # registries
        'AdapterV2': '0x240315db938d44bb124ae619f5fd0269a02d1271',
        'AdapterIronBank': '0xff0bd2d0c7e9424ccb149ed3757155eef41a793d',
        #
        # tvls
        'TvlV2': '0x14d6e0908bae40a2487352b2a9cb1a6232da8785',
        'TvlV1': '0xf4fb8903a41fc78686b26de55502cde42a4c6c78',
        'TvlIronBank': '0xec7ac8ac897f5082b2c3d4e8d2173f992a097f24',
        'TvlEarn': '0x1007ed6fdfac72bbea9c719cf1fa9c355d248691',
        'TvlveCRV': '0x560144c25e53149ac410e5d33bdb131e49a850e5',
        #
        # helpers
        'Helper': '0x5aacd0d03096039ac4381cd814637e9fb7c34a6f',
        'UniqueAddressesHelper': '0xc3a0bef4a47ba579cbba510ae2c59d9b9bf9467c',
        'StrategiesHelper': '0xae813841436fe29b95a14ac701afb1502c4cb789',
        'AllowancesHelper': '0x4218e20db87023049fc582aaa4bd47a3611a20ab',
        'AddressMergeHelper': '0x957e3ae7983155a9f9e08da555b8084448be26e4',
        'PricesHelper': '0x5d63a8584d91ebc5033d022afd6c5a7c7fddc99b',
        'BalancesHelper': '0x855ffe28019106d089bc018df18838f8d241c402',
        #
        # generators
        'AddressesGeneratorV1Vaults': '0xce29d34c8e88a2e1edde10ad4eee4f3e379fc041',
        'AddressesGeneratorV2Vaults': '0x437758d475f70249e03eda6be23684ad1fc375f0',
        'AddressesGeneratorEarn': '0xf536399c04683d7ab0bcb1308c245b4bbb539344',
        'AddressesGeneratorIronBank': '0xa0b57619a980dfefd50f24f310ee1b55a40a9d46',
        #
        # delegation mapping
        'DelegatedBalanceMapping': '0xc01a529c01f9399c928a4afc50e25f12d1e5b142',
        #
        # calculations
        'CalculationsCurve': '0xe9cff16bdac9729f18cbac451ecca6c50b372207',
        'CalculationsIronBank': '0x55e9b18fefff7e00548d54480373fc8843de8ea4',
        'CalculationsSushiswap': '0x88de7d7f7b9597c86b8cd195374fbf602934f334',
        'CalculationsYearnVaults': '0x38477f2159638956d33e18951d98238a53b9aa3c',
        #
        # registries
        'RegistryEarn': '0x62a4e0e7574e5407656a65cc8dbdf70f3c6eb04b',
        'RegistryV2': '0x50c1a2ea0a861a967d9d0ffe2ae4012c2e053804',
        'RegistryV1': '0x3ee41c098f9666ed2ea246f4d2558010e59d63a0',
        'RegistryIB': '0xab1c342c7bf5ec5f02adea1c2270670bca144cbb',
    }

    return mainnnet_addresses


def get_yearn_address(
    name: str,
    network: spec.NetworkReference,
) -> spec.Address:

    addresses = get_yearn_addresses(network=network)
    return addresses[name]


#
# # address printing
#


def print_lens_addresses(network: spec.NetworkReference) -> None:
    addresses = get_yearn_addresses(network=network)
    rows = []
    for name, address in addresses.items():
        row = [name, address]
        rows.append(row)
    labels = [
        'name',
        'address',
    ]
    styles = cli.get_cli_styles()
    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'name': styles['option'],
            'address': styles['metavar'],
        },
        indent=4,
    )


def print_vault_addresses(
    api_vaults: typing.Sequence[yearn_spec.ApiVault], verbose: bool = False
) -> None:
    if verbose:
        _print_vault_addresses_verbose(api_vaults=api_vaults)
    else:
        _print_vault_addresses_nonverbose(api_vaults=api_vaults)


def _print_vault_addresses_nonverbose(
    api_vaults: typing.Sequence[yearn_spec.ApiVault],
) -> None:
    rows = []
    for datum in api_vaults:
        row = [
            datum['name'],
            datum['address'].lower(),
        ]
        rows.append(row)

    labels = [
        'vault',
        'address',
    ]
    sort_index = labels.index('vault')
    rows = sorted(rows, key=lambda row: row[sort_index])

    styles = cli.get_cli_styles()
    toolstr.print_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'vault': styles['option'],
            'address': styles['metavar'],
        },
        indent=4,
    )


def _print_vault_addresses_verbose(
    api_vaults: typing.Sequence[yearn_spec.ApiVault],
) -> None:

    styles = cli.get_cli_styles()

    rows = []
    for datum in api_vaults:

        addresses = {
            'vault': datum['address'],
            'underlying': datum['token']['address'],
        }
        for s, strategy in enumerate(datum['strategies']):
            addresses['strategy ' + str(s)] = strategy['address']
        address_pieces = [
            toolstr.add_style(name, styles['comment'])
            + ' '
            + toolstr.add_style(address.lower(), styles['metavar'])
            for name, address in addresses.items()
        ]

        row = [datum['name'], '\n'.join(address_pieces)]
        rows.append(row)

    labels = [
        'vault',
        'address',
    ]
    sort_index = labels.index('vault')
    rows = sorted(rows, key=lambda row: row[sort_index])

    toolstr.print_multiline_table(
        rows,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'vault': styles['description'],
            'address': styles['metavar'],
        },
    )
