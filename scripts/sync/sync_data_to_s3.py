#!/usr/bin/env python3

import argparse
import os
import subprocess

from ctc import config_utils


command_template = 'aws s3 sync {local_path} {s3_uri}'

# parse inputs
parser = argparse.ArgumentParser()
parser.add_argument('--dry', action='store_true')
parser.add_argument('--test', action='store_true')
parser.add_argument('--local_path')
parser.add_argument('--s3_uri')
args = parser.parse_args()
dry = args.dry
test = args.test
local_path = args.local_path
s3_uri = args.s3_uri

# parse local path
config = config_utils.get_config()
data_root = config['data_root']
if local_path is None:
    local_path = data_root
local_path = os.path.abspath(local_path)
if not local_path.startswith(data_root):
    raise Exception('local_path is outside of data_root')

# parse s3 uri
if s3_uri is None:
    s3_root = 's3://analysis-fei/'
    local_relpath = os.path.relpath(local_path, data_root)
    s3_uri = os.path.join(s3_root, local_relpath)

# build command
if test:
    s3_uri = s3_uri + 'test/'
command = command_template.format(local_path=local_path, s3_uri=s3_uri)
if dry:
    command = command + ' --dryrun'

print('performing sync')
print('- local_path:', local_path)
print('- s3_uri:', s3_uri)
print('- dry:', dry)
print('- test:', test)
print()

# sync
subprocess.call(command, shell=True)

