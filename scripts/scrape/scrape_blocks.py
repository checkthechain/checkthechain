#!/usr/bin/env python3
from ctc import evm
from ctc import config_utils
from ctc.toolbox import etl_utils


#
exported = etl_utils.list_exported_data('blocks', 'block_timestamps')
start_block = exported['end_block'] + 1
end_block = evm.get_block_number('latest')

print('exporting blocks')
print('start_block:', start_block)
print('end_block:', end_block)

# export blocks
etl_utils.export_blocks(
    provider=config_utils.get_config()['export_provider'],
    start_block=start_block,
    end_block=end_block,
    etl_view='raw',
)

# export block timestamps
etl_utils.extract_block_timestamps()

