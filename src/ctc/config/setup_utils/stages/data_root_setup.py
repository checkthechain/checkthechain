from __future__ import annotations

import os
import shutil
import typing

import toolcli

from ... import config_defaults


def setup_data_root(
    styles: dict[str, str],
    old_config: typing.Mapping[typing.Any, typing.Any],
) -> str:

    print()
    print()
    toolcli.print('## Data Root Directory', style=styles['header'])
    print()

    new_data_root = None

    # decide whether to use old data root
    old_data_root: str | None = old_config.get('data_dir')
    if old_data_root is not None and not isinstance(old_data_root, str):
        old_data_root = None
    if isinstance(old_data_root, str):
        old_data_root = os.path.abspath(old_data_root)
        if os.path.isdir(old_data_root):
            prompt = 'Continue using data directory ' + str(old_data_root) + '? '
            if toolcli.input_yes_or_no(prompt, default='yes'):
                new_data_root = old_data_root
            else:
                print(
                    'OK. You can specify whether to keep this old data'
                    ' after a new directory is chosen'
                )

    # enter new data root
    if new_data_root is None:
        new_data_root = toolcli.input_directory_path(
            prompt='Where should ctc store data? (specify a directory path)',
            default=config_defaults.get_default_data_dir(),
            require_absolute=True,
            must_already_exist=False,
            create_directory=False,
            style=styles['question'],
        )

        # move old data
        if isinstance(old_data_root, str) and os.path.isdir(old_data_root):
            prompt = 'Move old ctc data to this new location?'
            answer = toolcli.input_yes_or_no(prompt, default='yes')
            if answer:
                if not os.path.isdir(new_data_root):
                    shutil.move(old_data_root, new_data_root)

    # create files and subdirectories and upgrade if need be
    initialize_data_root(new_data_root)

    return new_data_root


def initialize_data_root(path: str) -> None:
    pass
