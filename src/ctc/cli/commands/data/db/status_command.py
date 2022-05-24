from __future__ import annotations

import toolcli

from ctc import config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': status_command,
        'help': 'display database status',
    }


def status_command() -> None:
    db_config = config.get_db_config()

    # display currently existing database tables
    # display missing tables
    # display number of rows in each table
    # display schema version of each table
    print(db_config)

    # which networks is db currently created for?
    # is db created for default network?
