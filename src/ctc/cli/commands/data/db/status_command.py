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
    toolstr.print_header('Database Config')
    print('- dbms:', db_config['dbms'])
    if db_config['dbms'] == 'sqlite':
        print('- path:', db_config['path'])
    else:
        raise NotImplementedEror()

    print()
    toolstr.print_header('Data to Store')
    networks = config.get_used_networks()
    datatypes = db.get_all_datatypes()
    print('- networks')
    for network in networks:
        print('    -', network)
    print('- schemas')
    for datatype in datatypes:
        print('    -', datatype)

    print()
    db_exists = toolsql.does_db_exist(db_config=db_config)
    if db_exists:
        db_schema = db.get_complete_prepared_schema()
        toolsql.print_schema(db_config=db_config, db_schema=db_schema)
    else:
        toolstr.print_text_box('Schema Summary')
        print('- db does not exist')
