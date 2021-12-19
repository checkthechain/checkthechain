import os

from ctc import config_utils


def get_command_spec():
    return {
        'f': config_command,
    }


def config_command():

    env_var = config_utils.config_path_env_var

    print('# Config Summary')
    print('- config env variable:', env_var)
    if env_var not in os.environ:
        print('-', env_var, 'not set')
    else:
        env_value = os.environ[env_var]
        if env_value is None or env_value == '':
            print('-', env_var, 'set to null')
        else:
            print('-', env_var, 'set to:', env_value)

    print()
    print('## Config Values')
    config = config_utils.get_config()
    for key in sorted(config.keys()):
        print('-', str(key) + ':', config[key])

