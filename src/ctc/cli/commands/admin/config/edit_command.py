from __future__ import annotations

import json
import os
import shutil
import tempfile

import toolcli
import toolstr

from ctc import cli
import ctc.config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': edit_config_command,
        'help': 'edit config values',
        'hidden': True,
        'examples': [''],
    }


def edit_config_command() -> None:
    import subprocess

    editor = os.environ.get('EDITOR')
    if editor is None or editor == '':
        editor = 'editor'
        print('$EDITOR env var not set, attempting to use default editor')

    config_path = ctc.config.get_config_path()

    styles = cli.get_cli_styles()
    toolstr.print('editing config in editor', style=styles['description'])
    cli.print_bullet(key='editor', value=editor)
    cli.print_bullet(key='config_path', value=config_path)
    print()

    tempdir = tempfile.mkdtemp()
    temppath = os.path.join(tempdir, 'config.json')
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    with open(temppath, 'w') as f:
        json.dump(config_data, f, indent=4, sort_keys=True)
    subprocess.call([editor, temppath])
    shutil.copy2(temppath, config_path)
    print('done editing config')
