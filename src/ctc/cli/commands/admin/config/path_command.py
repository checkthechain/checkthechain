from ctc import config


def get_command_spec():
    return {
        'f': path_command,
        'help': 'print config path',
    }


def path_command():
    print(config.get_config_path())

