#!/usr/bin/env python3

import subprocess

from fei import config_utils


config = config_utils.get_config()
data_root = config['data_root']
backup_dir = config['backup_dir']

cmd_template = 'rsync -ravhp {data_root} {backup_dir}'
cmd = cmd_template.format(data_root=data_root, backup_dir=backup_dir)

subprocess.call(cmd, shell=True)

