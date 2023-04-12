from __future__ import annotations

import toolcli
import toolsql

import ctc


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': login_command,
        'help': 'login to database with interactive shell',
        'examples': [''],
    }


def login_command() -> None:
    db_config = ctc.config.get_db_config('main')
    toolsql.login(db_config)

