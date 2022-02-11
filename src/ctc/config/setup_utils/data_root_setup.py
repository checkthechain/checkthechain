from __future__ import annotations

import os

import toolcli

from .. import config_data
from .. import config_read


def setup_data_root(styles: dict[str, str]) -> tuple[str, bool]:

    print()
    print()
    toolcli.print('## Data Root Directory', style=styles['header'])

    input_kwargs: toolcli.InputFilenameOrDirectoryKwargs = {
        'prompt': 'Where should ctc store data? (specify a directory path)\n> ',
        'create_directory': 'prompt_and_require',
        'style': styles['question'],
    }

    if config_read.config_path_exists():
        try:
            config = config_read.get_config(validate=False)
            old_data_root = config['data_dir']
        except Exception:
            old_data_root = None
    else:
        old_data_root = None

    # data_root
    if old_data_root is None:
        print()
        new_data_root = toolcli.input_filename_or_directory(**input_kwargs)
        create_new_config = True

    else:
        print()
        toolcli.print(
            'Data directory currently set to:',
            toolcli.add_style(old_data_root, styles['path']),
        )

        if not isinstance(old_data_root, str):
            print()
            print('This value is invalid')
            print()
            new_data_root = toolcli.input_filename_or_directory(**input_kwargs)
            create_new_config = True

        elif os.path.abspath(old_data_root) != old_data_root:
            print()
            print('This path should be an absolute path')
            print()
            print('Absolute path:', os.path.abspath(old_data_root))
            print()
            if toolcli.input_yes_or_no('Use this path for data directory?'):
                new_data_root = old_data_root
                create_new_config = False
            else:
                print()
                new_data_root = toolcli.input_filename_or_directory(
                    **input_kwargs
                )
                create_new_config = True

        else:
            print()
            if toolcli.input_yes_or_no(
                'Keep storing data in this directory? ',
                style=styles['question'],
                default='yes',
            ):
                new_data_root = old_data_root
                create_new_config = False
            else:
                new_data_root = toolcli.input_filename_or_directory(
                    **input_kwargs
                )
                create_new_config = True

    # initialize directory data
    if config_data.is_data_root_initialized(new_data_root):
        print()
        print('Data directory is already initialized')
    else:
        initialized = config_data.initialize_data_root(new_data_root)
        if not initialized:
            return setup_data_root(styles=styles)

    return new_data_root, create_new_config

