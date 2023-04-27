from __future__ import annotations

import typing

import aiohttp
import toolcli
import toolstr
import toolsql

from ctc import cli
from ctc import db
from ctc import spec
from ... import config_defaults


def setup_dbs(
    *,
    styles: toolcli.StyleTheme,
    data_dir: str,
    network_data: spec.PartialConfig,
    headless: bool,
    old_db_configs: typing.Mapping[str, toolsql.DBConfig] | None = None,
) -> spec.PartialConfig:
    print()
    print()
    toolstr.print('## Database Setup', style=styles['title'])
    print()
    print('ctc stores its collected chain data in an sql database')

    # decide whether to use old config
    if old_db_configs is not None and old_db_configs.get('main') is not None:
        old_db_config = old_db_configs['main']
    else:
        old_db_config = None
    if old_db_config is not None:
        print()
        print('Current database config:')
        for key, value in old_db_config.items():
            if key == 'password':
                value = '********'
            cli.print_bullet(key=key, value=value)
        print()
        answer = toolcli.input_yes_or_no(
            prompt='Continue using this database configuration? ',
            default='yes',
            style=styles['metavar'],
            headless=headless,
        )
        if answer:
            db_configs = old_db_configs
        else:
            db_configs = None
    else:
        db_configs = None

    # initialize new config if old one not used
    if db_configs is None:
        print()
        dbms_choices = ['sqlite', 'postgresql']
        dbms_index = toolcli.input_number_choice(
            prompt='Which database do you want to use?\nuse sqlite for easy setup, use postgresql if in cloud',
            choices=dbms_choices,
            style=styles['metavar'],
            headless=headless,
            default='sqlite',
        )
        default_dbms = dbms_choices[dbms_index]
        if default_dbms == 'sqlite':
            db_configs = config_defaults.get_default_db_configs(
                data_dir=data_dir
            )
        else:
            db_configs = _get_postgres_config(headless=headless, styles=styles)

    # check database versions
    check_db_versions(list(db_configs.values()))

    # create db
    print()
    for db_config in db_configs.values():
        toolsql.create_db(
            db_config=db_config,
            db_schema=None,
            if_not_exists=True,
            verbose=True,
            confirm=True,
        )

    print()
    try:
        _delete_incomplete_chainlink_schemas(db_configs['main'])
    except toolsql.CannotConnect:
        pass

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

    with toolsql.connect(db_configs['main']) as conn:
        db.create_missing_tables(
            networks=list(used_networks),
            conn=conn,
            confirm=True,
        )

    return {'db_configs': db_configs}


def _get_postgres_config(
    headless: bool,
    styles: toolcli.StyleTheme,
) -> typing.Mapping[str, toolsql.DBConfig]:
    print()
    print('Setting up PostgreSQL...')
    hostname = toolcli.input_prompt(
        'What is the hostname ',
        default='localhost',
        style=styles['metavar'],
        headless=headless,
    )
    port = toolcli.input_int(
        'What is the port? ',
        default='5432',
        style=styles['metavar'],
        headless=headless,
    )
    database = toolcli.input_prompt(
        'What is the database name ',
        default='ctc',
        style=styles['metavar'],
        headless=headless,
    )
    username = toolcli.input_prompt(
        'What is the username? ',
        default='postgres',
        style=styles['metavar'],
        headless=headless,
    )
    password = toolcli.input_prompt(
        'What is the password? ',
        default='',
        style=styles['metavar'],
        headless=headless,
    )
    db_config: toolsql.DBConfig = {
        'dbms': 'postgresql',
        'database': database,
        'hostname': hostname,
        'port': port,
        'username': username,
        'password': password,
    }

    return {'main': db_config}


async def async_populate_db_tables(
    db_config: toolsql.DBConfig,
    styles: toolcli.StyleTheme,
) -> None:
    from ctc.protocols.chainlink_utils import chainlink_db
    from ..default_data import default_erc20s

    print()
    print()
    toolstr.print('## Populating Database', style=styles['title'])

    # populate data: erc20s
    print()
    print('Populating database with metadata of common ERC20 tokens...')
    print()
    await default_erc20s.async_intake_default_erc20s(
        context=dict(network='ethereum'),
    )

    # populate data: chainlink
    print()
    print('Populating database with latest Chainlink oracle feeds...')
    print()
    try:
        await chainlink_db.async_import_networks_to_db(db_config=db_config)
    except aiohttp.client_exceptions.ClientConnectorError:
        print('Could not connect to Chainlink server, skipping')
    except Exception:
        print('Could not add feeds to db, skipping')


def _delete_incomplete_chainlink_schemas(db_config: toolsql.DBConfig) -> None:
    """detect any tables missing in chainlink schema

    this is a stopgap until a more comprehensive migration system is in place
    """

    from ctc import db

    # looking for schemas that have already been created, but are missing tables
    networks = list(config_defaults.get_default_networks_metadata().keys())
    with toolsql.connect(db_config) as conn:
        table_names = toolsql.get_table_names(conn)
        if 'schema_versions' not in table_names:
            return
        for network in networks:
            context: spec.Context = {'network': network}
            schema_version = db.get_schema_version(
                schema_name='chainlink',
                context=dict(network=network),
                conn=conn,
            )
            if schema_version is not None:
                schema = db.get_prepared_schema(
                    schema_name='chainlink', context=context
                )
                for table_name in schema['tables'].keys():
                    if table_name not in table_names:
                        print(
                            'missing chainlink_aggregator_updates table, rebuilding schema'
                        )
                        db.drop_schema(
                            schema_name='chainlink',
                            context=context,
                            confirm=True,
                            conn=conn,
                        )


def check_db_versions(db_configs: typing.Sequence[toolsql.DBConfig]) -> None:
    dbms_set = {db_config.get('dbms') for db_config in db_configs}
    for dbms in dbms_set:
        # check sqlite
        if dbms == 'sqlite':
            import sqlite3

            # get sqlite3 version
            if sqlite3.sqlite_version.count('.') == 2:
                major_str, minor_str, _ = sqlite3.sqlite_version.split('.')
            elif sqlite3.sqlite_version.count('.') == 1:
                major_str, minor_str = sqlite3.sqlite_version.split('.')
            else:
                major_str, minor_str = '0', '0'
            major = int(major_str)
            minor = int(minor_str)

            if (major < 3) or (major == 3 and minor < 24):
                raise Exception(
                    'ctc requires sqlite verison >= 3.24. This environment is using sqlite version '
                    + str(sqlite3.sqlite_version)
                    + '. You must upgrade sqlite3 before continuing.'
                    + ' If using apt, this can be accomplished using `apt install sqlite3` or `sudo apt-get install sqlite3`'
                )

        elif dbms == 'postgresql':
            pass

        else:
            raise Exception('dbms not supported: ' + str(dbms))

