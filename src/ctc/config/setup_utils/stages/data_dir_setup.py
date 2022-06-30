from __future__ import annotations

import os
import shutil
import typing

import toolcli
import toolstr

from ctc import spec
from ... import config_defaults
from .. import data_dir_versioning


def setup_data_dir(
    styles: dict[str, str],
    old_config: typing.Mapping[typing.Any, typing.Any],
) -> spec.PartialConfig:

    print()
    print()
    toolstr.print('## Data Root Directory', style=styles['header'])
    print()

    new_data_root = None

    # decide whether to use old data root
    old_data_root: str | None = old_config.get('data_dir')
    if old_data_root is not None and not isinstance(old_data_root, str):
        old_data_root = None
    if isinstance(old_data_root, str):
        old_data_root = os.path.abspath(os.path.expanduser(old_data_root))
        if os.path.isdir(old_data_root):
            prompt = (
                'Continue using data directory ['
                + styles['path']
                + ']'
                + str(old_data_root)
                + '[/'
                + styles['path']
                + ']? '
            )
            if toolcli.input_yes_or_no(
                prompt,
                default='yes',
                style=styles['question'],
            ):
                new_data_root = old_data_root
            else:
                print(
                    'OK. You can specify whether to keep this old data'
                    ' after a new directory is chosen'
                )

    # enter new data root
    if new_data_root is None:
        new_data_root = toolcli.input_directory_path(
            prompt='Where should ctc store data? (specify a directory path) ',
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
    data_dir_versioning.initialize_data_subdirs(new_data_root, version='0.3.0')

    print()
    prompt = 'Do you want to disable ctc logging? '
    disable_logs = toolcli.input_yes_or_no(
        prompt, default='no', style=styles['question']
    )

    return {
        'data_dir': new_data_root,
        'log_rpc_calls': not disable_logs,
        'log_sql_queries': not disable_logs,
    }
