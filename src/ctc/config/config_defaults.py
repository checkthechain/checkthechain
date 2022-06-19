from __future__ import annotations

import os


def get_default_data_dir() -> str:
    return os.path.abspath(os.path.join(os.path.expanduser('~'), 'ctc_data'))
