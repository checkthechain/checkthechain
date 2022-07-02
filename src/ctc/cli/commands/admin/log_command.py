"""

TODO:
- tail all log files or select which files to tail
    - https://unix.stackexchange.com/questions/149017/how-to-tail-multiple-files-using-tail-0f-in-linux-aix
"""

from __future__ import annotations

import os
import subprocess

import toolcli

from ctc import config


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': log_command,
        'help': 'display logs',
        'args': [],
        'examples': {'': {'description': 'tail logs', 'runnable': False}},
    }


def log_command() -> None:
    rpc_requests_log_path = config.get_rpc_requests_log_path()
    print('watching log file:', rpc_requests_log_path)
    try:
        n_lines = os.get_terminal_size().lines - 3
        subprocess.call(
            ['tail', '-n', str(n_lines), '-f', rpc_requests_log_path]
        )
    except KeyboardInterrupt:
        print()
