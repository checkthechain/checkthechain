import os

import ctc.config


def get_command_spec():
    return {
        'f': cd_command,
        'args': [
            {'name': 'dirname'},
        ],
        'special': {'cd': True},
    }


def cd_command(dirname, new_dir_tempfile):

    if new_dir_tempfile is None:
        raise Exception('must specify new_dir_tempfile')

    if dirname == 'code':
        path = ctc.__path__[0]

    elif dirname == 'data':
        path = ctc.config.get_data_dir()

    elif dirname == 'default_data':
        path = ctc.config.get_default_data_dir()

    elif dirname == 'config':
        path = os.path.dirname(ctc.config.get_config_path())

    elif dirname == 'reports':
        path = ctc.config.get_reports_dir()

    else:
        raise Exception('unknown directory: ' + str(dirname))

    with open(new_dir_tempfile, 'w') as f:
        f.write(path)

