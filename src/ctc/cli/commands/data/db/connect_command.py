import subprocess

from ctc import config


def get_command_spec():
    return {
        'f': connect_command,
        'help': 'connect to database console (proceed with caution)',
    }


def connect_command():
    db_config = config.get_db_config()
    if db_config is None:
        print('no database is configured, run `ctc setup`')
        return

    if db_config['dbms'] == 'sqlite':
        print(
            'connecting to',
            db_config['dbms'],
            'database at path',
            db_config['path'],
        )
        subprocess.call(['sqlite3', db_config['path']])
    else:
        raise Exception('unknown dbms')

