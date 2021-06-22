#!/usr/bin/env python3

from fei.data import web3_utils
from fei.data import etl
import fei.report


chunk_size = 1000

# determine block range
exported_data = etl.list_exported_data('blocks', 'raw')
last_exported_block = max(exported_data['mask_index'])
start_block = last_exported_block + 1
latest_block_number = web3_utils.fetch_latest_block_number()
end_block = int(latest_block_number / chunk_size) * chunk_size - 1

# output
print('last_exported_block:', fei.report.int_to_str(last_exported_block))
print('latest_block_number:', fei.report.int_to_str(latest_block_number))
print('        start_block:', fei.report.int_to_str(start_block))
print('          end_block:', fei.report.int_to_str(end_block))
print()

# export chunks
if start_block < end_block:
    etl.export_as_chunks(start_block, end_block)
else:
    wait_until = fei.report.int_to_str(end_block + chunk_size)
    print('not scraping yet, wait until block', wait_until)

