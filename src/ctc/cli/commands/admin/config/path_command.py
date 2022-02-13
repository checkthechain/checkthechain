from ctc import config


def get_command_spec():
    return {
        'f': path_command,
    }


def path_command():
    print(config.get_config_path())

