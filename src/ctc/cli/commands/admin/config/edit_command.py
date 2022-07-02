from __future__ import annotations

import toolcli

import os

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

    print('editing config in editor')
    print('- editor:', editor)
    print('- config_path:', config_path)
    print()
    subprocess.call([editor, config_path])
    print('done editing config')
