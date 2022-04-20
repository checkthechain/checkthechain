from __future__ import annotations

import json
import os
import typing

import toolcli

from ctc import spec

if typing.TYPE_CHECKING:
    import toolsql


def setup_dbs(
    styles: typing.Mapping[str, str],
    data_root: str,
    old_config: typing.Mapping,
) -> tuple[spec.PartialConfigSpec, bool]:
    print()
    print()
    toolcli.print('## Database Setup', style=styles['header'])
    print()
    print('ctc can store chain data to a sql database')
    print()
    print('Doing this will significantly increase overall performance')
    print()
    choices = [
        'sqlite database in ctc data directory',
        'sqlite database in a custom directory',
        'postgresql database',
        'do not use a database',
    ]
    db_mode = toolcli.input_number_choice(
        prompt='Which database setup do you want to use?',
        choices=choices,
        default=choices[0],
        style=styles['question'],
    )

    db_configs: typing.MutableMapping[str, 'toolsql.DBConfig'] = {}
    if db_mode == 0:
        db_configs['main'] = {
            'dbms': 'sqlite',
            'path': os.path.join(data_root, 'ctc.db'),
        }
    elif db_mode == 1:
        path = toolcli.input(
            prompt='Enter path where sqlite database be stored: '
        )
        if path.endswith('.db'):
            filepath = path
        else:
            if os.path.isdir(path):
                filepath = os.path.join(path, 'ctc.db')
            else:
                answer = toolcli.input_yes_or_no(
                    'Directory does not exist. Create it? '
                )
                if not answer:
                    raise Exception()
                else:
                    os.makedirs(path, exist_ok=True)
                    filepath = os.path.join(path, 'ctc.db')

        if os.path.isfile(filepath):
            answer = toolcli.input_yes_or_no(
                'Database already exists. ctc will create tables in database if needed. Proceed? '
            )
            if not answer:
                raise Exception('must use database')

        db_configs['main'] = {
            'dbms': 'sqlite',
            'path': filepath,
        }

    elif db_mode == 2:
        print('Must connect to a pre-existing postgresql database')
        print('(ctc will create tables in this database if needed)')
        print()
        url = toolcli.input(prompt='What is the postgresql database url? ')
        username = toolcli.input(
            prompt='What is the postgresql database username? '
        )
        password = toolcli.input(
            prompt='What is the postgresql database password? '
        )
        db_configs['main'] = {
            'dbms': 'postgresql',
            'hostname': url,
            'username': username,
            'password': password,
        }
    elif db_mode == 3:
        print('no database will be used')
    else:
        raise Exception('unknown option')

    write_config = json.dumps(db_configs, sort_keys=True) != json.dumps(
        old_config.get('db_config'), sort_keys=True
    )

    return {'db_configs': db_configs}, write_config

