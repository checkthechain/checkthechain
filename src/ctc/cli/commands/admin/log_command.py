"""

TODO:
- tail all log files or select which files to tail
    - https://unix.stackexchange.com/questions/149017/how-to-tail-multiple-files-using-tail-0f-in-linux-aix
"""

import os
import subprocess

from ctc import config


def get_command_spec():
    return {
        'f': log_command,
        'help': 'display logs',
        'args': [
        ],
    }


def log_command():
    rpc_requests_log_path = config.get_rpc_requests_log_path()
    print('watching log file:', rpc_requests_log_path)
    try:
        n_lines = os.get_terminal_size().lines - 3
        subprocess.call(['tail', '-n', str(n_lines), '-f', rpc_requests_log_path])
    except KeyboardInterrupt:
        print()

