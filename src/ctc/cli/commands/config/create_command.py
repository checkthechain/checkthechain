import json
import os

import ctc.config


def get_command_spec():
    return {
        'f': create_config_command,
        'args': [
            {'name': '--provider'},
            {'name': '--path'},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
        ],
    }


def create_config_command(provider, path, overwrite):

    if provider is None:
        provider = input('Provider URL? ')

    env_var = ctc.config.config_path_env_var
    if path is None:
        if env_var not in os.environ or os.environ.get(env_var) in ['', None]:
            print(env_var, 'not set')
            path = input('Where should config be stored? ')
            print()
        else:
            path = os.environ[env_var]

    print('path:', path)
    if os.path.exists(path) and not overwrite:
        raise Exception('config already exists, use --overwrite')

    print()
    print('Creating config...')
    print('- provider:', provider)
    print('- path:', path)

    config_data = {'export_provider': provider}
    with open(path, 'w') as f:
        json.dump(config_data, f)

    print()
    print('Config created')
    if os.environ.get(env_var) != path:
        print()
        print('Make sure to set', env_var, 'equal to', path, 'in your environment')

