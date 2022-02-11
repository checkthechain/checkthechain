from __future__ import annotations

import os

import toolcli

from .. import config_read
from .. import config_spec


def setup_config_path(styles: dict[str, str]) -> tuple[str, bool]:
    # TODO: for each "where" question offer a default path
    # e.g. ~/.config/ctc/config.json

    env_var = config_spec.config_path_env_var
    env_var_value = os.environ.get(env_var)
    default_config_path = config_spec.default_config_path
    old_config_path = config_read.get_config_path(raise_if_dne=False)

    input_kwargs: toolcli.InputFilenameOrDirectoryKwargs = {
        'prompt': 'Where should config be created? Specify a file path or directory path',
        'default_directory': default_config_path,
        'default_filename': 'config.json',
        'style': styles['question'],
    }

    print()
    print()
    toolcli.print('## Config Path', style=styles['header'])

    if os.path.isfile(old_config_path):
        # case: config file already exists

        # print config path source
        if env_var_value not in [None, '']:
            print()
            print(env_var, '=', env_var_value)
        elif old_config_path == default_config_path:
            print()
            toolcli.print(
                'Using default config path',
                toolcli.add_style(default_config_path, style=styles['path']),
            )
        else:
            raise Exception('unknown config path source')
        print()
        print('Config already file exists')

        # ask whether to change config path
        print()
        answer = toolcli.input_yes_or_no(
            'Keep config at this location? ',
            default='yes',
            style=styles['question'],
        )
        if answer:
            new_config_path = old_config_path
            create_new_config = False
        else:
            print()
            new_config_path = toolcli.input_filename_or_directory(
                **input_kwargs
            )
            create_new_config = True

    elif not os.path.isfile(old_config_path):
        # case: config file does not exist

        if env_var_value not in [None, '']:
            # case: set by env var
            print()
            print(env_var, '=', env_var_value)
            print()
            print('Config path is set but config file does not exist')
            print()
            answer = toolcli.input_yes_or_no(
                'Create config at this path? ', style=styles['question']
            )

        else:
            # case: set by default
            print('Environmental variable', env_var, 'not set')
            print()
            answer = toolcli.input_yes_or_no(
                prompt='Use default config location? '
                + default_config_path + ' ',
                default='yes',
                style=styles['question'],
            )

        # ask whether to change config path
        if answer:
            new_config_path = old_config_path
        else:
            print()
            new_config_path = toolcli.input_filename_or_directory(
                **input_kwargs
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

