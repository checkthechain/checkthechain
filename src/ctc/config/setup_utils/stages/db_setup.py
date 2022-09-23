from __future__ import annotations

import os
import typing

import aiohttp
import toolstr
import toolsql

from ctc import db
from ctc import spec
from ... import config_defaults


def setup_dbs(
    *,
    styles: typing.Mapping[str, str],
    data_dir: str,
    network_data: spec.PartialConfig,
    db_config: toolsql.DBConfig | None = None,
) -> spec.PartialConfig:

    print()
    print()
    toolstr.print('## Database Setup', style=styles['header'])
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
            toolstr.print(
                'Creating database at path ['
                + styles['path']
                + ']'
                + db_path
                + '[/'
                + styles['path']
                + ']'
            )
        else:
            toolstr.print(
                'Existing database detected at path ['
                + styles['path']
                + ']'
                + db_path
                + '[/'
                + styles['path']
                + ']'
            )

    print()
    _delete_incomplete_chainlink_schemas()

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
    db.create_missing_tables(
        networks=list(used_networks),
        db_config=db_configs['main'],
        confirm=True,
    )

    return {'db_configs': db_configs}


async def async_populate_db_tables(
    db_config: toolsql.SAEngine,
    styles: typing.Mapping[str, str],
) -> None:
    from ctc.protocols.chainlink_utils import chainlink_db
    from ..default_data import default_erc20s

    engine = toolsql.create_engine(db_config=db_config)

    print()
    print()
    toolstr.print('## Populating Database', style=styles['header'])

    # populate data: erc20s
    print()
    print('Populating database with metadata of common ERC20 tokens...')
    print()
    await default_erc20s.async_intake_default_erc20s(
        network='mainnet',
        engine=engine,
    )

    # populate data: chainlink
    print()
    print('Populating database with latest Chainlink oracle feeds...')
    print()
    try:
        await chainlink_db.async_import_networks_to_db()
    except aiohttp.client_exceptions.ClientConnectorError:
        print('Could not connect to Chainlink server, skipping')
    except Exception:
        print('Could not add feeds to db, skipping')


def _delete_incomplete_chainlink_schemas() -> None:
    """detect any tables missing in chainlink schema

    this is a stopgap until a more comprehensive migration system is in place
    """

    from ctc import config
    from ctc import db
    from ctc import evm

    # looking for schemas that have already been created, but are missing tables
    metadata = toolsql.create_metadata_object_from_db(
        db_config=config.get_db_config()
    )
    if 'schema_versions' not in metadata.tables.keys():
        return
    for network in evm.get_networks():
        schema_version = db.get_schema_version(
            schema_name='chainlink', network=network
        )
        if schema_version is not None:
            schema = db.get_prepared_schema(
                schema_name='chainlink', network=network
            )
            for table_name in schema['tables'].keys():
                if table_name not in metadata.tables.keys():
                    print(
                        'missing chainlink_aggregator_updates table, rebuilding schema'
                    )
                    db.drop_schema(
                        schema_name='chainlink', network=network, confirm=True
                    )
