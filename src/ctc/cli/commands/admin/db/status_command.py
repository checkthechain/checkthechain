from __future__ import annotations

import toolcli
import toolstr
import toolsql

from ctc import config
from ctc import db


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': status_command,
        'help': 'display database status',
    }


def status_command() -> None:
    toolstr.print_text_box('Database Status')
    print()
    db_config = config.get_db_config()
    if db_config is None:
        print('[no db configured]')
        return

    toolstr.print_header('Database Config')
    print('- dbms:', db_config['dbms'])
    if db_config['dbms'] == 'sqlite':
        print('- path:', db_config['path'])
    else:
        raise NotImplementedError()

    # print data being stored
    active_schemas = db.get_active_schemas()
    print()
    toolstr.print_header('Data to Store')
    networks = config.get_used_networks()
    admin_schemas = db.get_admin_schema_names()
    generic_schemas = db.get_generic_schema_names()
    network_schemas = db.get_network_schema_names()
    print('- admin schemas')
    for admin_schema in admin_schemas:
        print('    -', admin_schema)
    print('- generic schemas')
    for generic_schema in generic_schemas:
        print('    -', generic_schema)
    print('- evm schemas')
    for datatype in network_schemas:
        if active_schemas.get(datatype):
            print('    -', datatype)
        else:
            print('    -', datatype, '(inactive)')
    print('- networks')
    for network in networks:
        print('    -', network)

    print()
    db_exists = toolsql.does_db_exist(db_config=db_config)
    if db_exists:
        db_schema = db.get_complete_prepared_schema()
        toolsql.print_schema(db_config=db_config, db_schema=db_schema)
    else:
        toolstr.print_text_box('Schema Summary')
        print('- db does not exist')
