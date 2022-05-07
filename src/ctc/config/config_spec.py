from __future__ import annotations

import os


config_path_env_var = 'CTC_CONFIG_PATH'

allowed_config_filetypes = ['.json']

default_config_path = os.path.expanduser('~/.config/ctc/config.json')

min_allowed_config_version = (0, 2, 10)
min_recommended_config_version = (0, 3, 0)
