from __future__ import annotations

import os
import typing

import aiohttp
import toolcli

from ctc import db
from ctc import spec
from ... import config_defaults


def setup_dbs(
    *,
    styles: typing.Mapping[str, str],
    data_dir: str,
    network_data: spec.PartialConfig,
) -> spec.PartialConfig:

    print()
    print()
    toolcli.print('## Database Setup', style=styles['header'])
    print()
    print('ctc stores its collected chain data in an sql database')

    db_configs = config_defaults.get_default_db_configs(data_dir)

    # create db
    print()
    for db_config in db_configs.values():
        if 'path' in db_config:
            db_path = db_config['path']
            db_dirpath = os.path.dirname(db_path)
            os.makedirs(db_dirpath, exist_ok=True)

        if not os.path.isfile(db_path):
            toolcli.print(
                'Creating database at path ['
                + styles['path']
                + ']'
                + db_path
                + '[/'
                + styles['path']
                + ']'
            )
        else:
            toolcli.print(
                'Existing database detected at path ['
                + styles['path']
                + ']'
                + db_path
                + '[/'
                + styles['path']
                + ']'
            )

    # create tables
    used_networks: set[spec.NetworkReference] = set()
    default_network = network_data.get('default_network')
    if default_network is not None:
        used_networks.add(default_network)
    for provider in network_data['providers'].values():
        network = provider.get('network')
        if network is not None:
            used_networks.add(network)
    used_networks = {
        network for network in used_networks if network is not None
    }
    print()
    db.create_evm_tables(networks=list(used_networks), confirm=True)

    return {'db_configs': db_configs}


async def async_populate_db_tables(styles: typing.Mapping[str, str]) -> None:
    from ctc.protocols import chainlink_utils
    from ..default_data import default_erc20s

    print()
    print()
    toolcli.print('## Populating Database', style=styles['header'])

    # populate data: erc20s
    print()
    print('Populating database with metadata of common ERC20 tokens...')
    print()
    await default_erc20s.async_intake_default_erc20s(network='mainnet')

    # populate data: chainlink
    print()
    print('Populating database with latest Chainlink oracle feeds...')
    print()
    try:
        await chainlink_utils.async_import_networks_to_db()
    except aiohttp.client_exceptions.ClientConnectorError:
        print('Could not connect to Chainlink server, skipping')
    except Exception:
        print('Could not add feeds to db, skipping')
