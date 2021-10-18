#!/usr/bin/env python3

import argparse

import toolstr

from ctc import evm
from ctc.toolbox import etl_utils


parser = argparse.ArgumentParser()
parser.add_argument('--dry', action='store_true')
args = parser.parse_args()
dry = args.dry


chunk_size = 1000

# determine block range
exported_data = etl_utils.list_exported_data('blocks', 'raw')
last_exported_block = max(exported_data['mask_index'])
start_block = last_exported_block + 1
latest_block_number = evm.fetch_latest_block_number()
end_block = int(latest_block_number / chunk_size) * chunk_size - 1

# output
if dry:
    print('!! [DRY RUN] !!')
print('last_exported_block:', toolstr.format(last_exported_block))
print('latest_block_number:', toolstr.format(latest_block_number))
print('        start_block:', toolstr.format(start_block))
print('          end_block:', toolstr.format(end_block))
print()

# export chunks
if start_block < end_block:
    etl_utils.export_as_chunks(start_block, end_block, dry=dry)
else:
    wait_until = toolstr.format(end_block + chunk_size)
    print('not scraping yet, wait until block', wait_until)

if dry:
    print('!! [DRY RUN] !!')

