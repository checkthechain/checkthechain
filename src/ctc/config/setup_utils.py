import json
import os

import toolcli

from ctc import spec
from . import config_spec
from . import config_utils


def setup_ctc() -> None:

    # print intro
    print('ctc initializing...')
    print()
    print('this process will make sure each of the following is completed:')
    print('- setup config path')
    print('- setup data directory')
    print('- setup networks and providers')
    print()
    print('each step can be skipped depending on what you need')

    # collect new config file data
    config_path, create_because_config_path = setup_config_path()
    data_root, create_because_data_root = setup_data_root()
    providers, create_because_provider = setup_providers()
    default_network, create_because_default_network = setup_default_network()
    network_metadata, create_because_network_metadata = setup_network_metadata()

    # create new config file if need be
    create_new_config = any(
        create_because_config_path,
        create_because_data_root,
        create_because_provider,
        create_because_network_metadata,
        create_because_default_network,
    )
    if create_new_config:
        config = {
            'data_root': data_root,
            'providers': providers,
            'default_network': default_network,
            'network_metadata': network_metadata,
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)
        print()
        print('config file created at:', config_path)

    # remind user to set env var
    if os.environ.get(config_spec.config_path_env_var) != config_path:
        print()
        print()
        print(
            'Remember to set your',
            config_spec.config_path_env_var,
            'environment variable to',
            config_path,
        )
        print()
        print(
            'For example, if using bash you can add the following line to ~/.profile:'
        )
        print()
        print(
            'export',
            config_spec.config_path_env_var
            + '="'
            + config_path.replace('"', '\\"')
            + '"',
        )

    # print outro
    print()
    print('Setup complete')


def setup_config_path() -> tuple[str, bool]:
    # TODO: for each "where" question offer a default path
    # e.g. ~/.config/ctc/config.json

    env_var = config_spec.config_path_env_var
    default_config_path = os.path.expanduser(
        os.path.join('~', '.config', 'ctc')
    )

    print()
    print()
    print('## Config Path')
    print()

    if not config_utils.config_path_is_set():
        print('Config path not set in', env_var)
        print()
        prompt = 'Where should config be created?'
        new_config_path = toolcli.input_prompt(
            prompt=prompt,
            default=default_config_path,
        )
        create_new_config = True

    elif not config_utils.config_path_exists():
        config_path = config_utils.get_config_path(raise_if_dne=False)
        print(env_var, '=', config_path)
        print()
        print('Config path is set but config file does not exist')
        print()
        answer = toolcli.input_yes_or_no('Create config at this path? ')
        if answer:
            new_config_path = config_path
        else:
            prompt = 'Where should config be created?'
            new_config_path = toolcli.input_prompt(
                prompt=prompt,
                default=default_config_path,
            )
        create_new_config = True

    else:
        config_path = config_utils.get_config_path()
        print('Config file exists')
        print(env_var, '=', config_path)
        print()
        answer = toolcli.input_yes_or_no('Keep config at this location?')
        if answer:
            new_config_path = config_path
            create_new_config = False
        else:
            prompt = 'Where should config be created?'
            new_config_path = toolcli.input_prompt(
                prompt=prompt,
                default=default_config_path,
            )
            create_new_config = True

    # check file extension
    if create_new_config:
        new_config_path = os.path.abspath(new_config_path)
        head, extension = os.path.splitext(new_config_path)
        default_extension = config_spec.allowed_config_filetypes[0]

        # if a directory, add file
        if extension == '':
            print()
            filename = 'config' + default_extension
            new_config_path = os.path.join(new_config_path, filename)
            print('This is a directory, will use', new_config_path)

        elif extension not in config_spec.allowed_config_filetypes:
            print()
            print(
                'File extension',
                extension,
                'not allowed, switching to',
                default_extension,
            )
            print()
            new_config_path = head + default_extension
            print(new_config_path)

    return new_config_path, create_new_config


def setup_data_root() -> tuple[str, bool]:

    print()
    print()
    print('## Data Root Directory')

    # data_root
    if not config_utils.config_path_exists():
        print()
        new_data_root = toolcli.input_prompt(
            prompt='Where should ctc store data? (specify a directory)\n'
        )
        create_new_config = True

    else:
        config = config_utils.get_config()
        data_root = config['data_root']
        print()
        print('Data directory currently set to:', data_root)

        if not isinstance(data_root, str):
            print('This value is invalid')
            print('Where should ctc store data? (specify a directory)')
            new_data_root = input()
            create_new_config = True

        elif os.path.abspath(data_root) != data_root:
            print('This path should be an absolute path')
            print()
            print('Absolute path:', os.path.abspath(data_root))
            if toolcli.input_yes_or_no('Use this path for data directory?'):
                new_data_root = data_root
                create_new_config = False
            else:
                new_data_root = toolcli.get_input_directory(
                    'Where should ctc store data? (specify a directory)'
                )
                create_new_config = True

        else:
            if toolcli.input_yes_or_no('Keep storing data in this directory?'):
                new_data_root = data_root
            else:
                new_data_root = toolcli.get_input_directory(
                    'Where should ctc store data? (specify a directory)'
                )

    # create directory if does not exist
    if not os.path.isdir(new_data_root):
        if toolcli.input_yes_or_no('Data directory does not exist, create it?'):


    # initialize directory data
    data_root_path = os.path.join(new_data_root, 'data_root.json')
    if not os.path.isfile(data_root_path):
        print('Initializing directory data')
        populate_initial_data(data_root=new_data_root)

    return new_data_root, create_new_config


def populate_initial_data():
    metadata = {
        'data_root_version': 0.1,
    }


def setup_providers() -> tuple[
    dict[spec.NetworkReference, spec.ProviderSpec], bool
]:
    # TODO: check if networks are known and valid
    if config_utils.config_exists():
        config = config_utils.get_config()
    else:
        config = None

    if config is not None:
        old_providers = config.get('providers')
        if not isinstance(old_providers, list):
            print()
            print('Current config value of providers is invaild')

        if len(providers) > 0:
            print()
            print('Current providers in config:')
            for network, provider in config['providers'].items():
                print('-', network + ':', provider)
        else:
            print()
            print('No providers currently specified in config')
    else:
        print('Would you like to add a provider?')
        print()

    print()
    print('Would you like to add more providers? ')


def setup_default_network() -> tuple[spec.NetworkName, bool]:
    if config_utils.config_exists():
        config = config_utils.get_config()
    else:
        config = None


def setup_network_metadata():
    pass

