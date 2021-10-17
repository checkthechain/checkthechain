import os

import humanfriendly
import pandas as pd

from ctc import config_utils
from ctc import directory
from .. import etl_list
from .. import etl_load


def extract_token_subsets(
    target_view,
    token_addresses,
    source_view='raw',
    verbose=True,
    start_block=None,
    end_block=None,
):
    """extract specific set of tokens from an etl dataset"""

    # determine range to extract
    if start_block is None or end_block is None:
        missing_range = _determine_latest_missing_extract_range(
            target_view=target_view, source_view=source_view
        )
        if start_block is None:
            start_block = missing_range[0]
        if end_block is None:
            end_block = missing_range[-1]
    if end_block < start_block:
        if verbose:
            print('no blocks in range')
        return

    data_kwargs = {
        'etl_view': 'raw',
        'start_block': start_block,
        'end_block': end_block,
    }

    output_paths = {}
    for rowtype in ['blocks', 'transactions', 'token_transfers']:
        output_paths[rowtype] = etl_list.get_path(
            rowtype,
            etl_view=target_view,
            start_block=data_kwargs['start_block'],
            end_block=data_kwargs['end_block'],
        )
        if os.path.isfile(output_paths[rowtype]):
            raise Exception('path already exists: ' + output_paths[rowtype])

    if verbose:
        print('extracting filtered receipts and logs')
        print('- tokens:')
        for token_address in token_addresses:
            print('    -', directory.address_to_symbol[token_address])
        print('- source_view:', source_view)
        print('- target_view:', target_view)
        print('- block export range:', start_block, end_block)
        print('- paths:')
        for rowtype, path in output_paths.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data_root = config_utils.get_config()['data_root']
            path = path.replace(data_root, '$DATA_ROOT')
            print('    -', rowtype + ':', path)
        print()

    exported_data = etl_list.list_exported_data(
        'token_transfers', **data_kwargs
    )
    paths = list(exported_data['path_ranges'].keys())

    #
    # # token transfers
    #

    if verbose:
        print('filtering token transfers...')
        print()
        _summarize_paths(paths, exported_data['path_ranges'])
        print()

    chunk_dfs = []
    for p, path in enumerate(paths):
        print(
            'chunk', p + 1, '/', len(paths), exported_data['path_ranges'][path]
        )
        chunk_df = pd.read_csv(path)
        chunk_df = chunk_df[chunk_df['token_address'].isin(token_addresses)]
        chunk_dfs.append(chunk_df)
    token_transfers_df = pd.concat(chunk_dfs, ignore_index=True)

    if verbose:
        print()
        print('saving token transfers...')
    token_transfers_df.to_csv(output_paths['token_transfers'], index=False)

    exported_data = etl_list.list_exported_data('transactions', **data_kwargs)
    paths = list(exported_data['path_ranges'].keys())
    transaction_hashes = set(token_transfers_df['transaction_hash'].values)
    del token_transfers_df

    #
    # # transactions
    #

    if verbose:
        print()
        print('filtering transactions...')
        print()
        _summarize_paths(paths, exported_data['path_ranges'])
        print()

    chunk_dfs = []
    for p, path in enumerate(paths):
        print(
            'chunk', p + 1, '/', len(paths), exported_data['path_ranges'][path]
        )
        chunk_df = pd.read_csv(path)
        chunk_df = chunk_df[chunk_df['hash'].isin(transaction_hashes)]
        chunk_dfs.append(chunk_df)
    transactions_df = pd.concat(chunk_dfs, ignore_index=True)

    if verbose:
        print()
        print('saving transactions...')
    transactions_df.to_csv(output_paths['transactions'], index=False)
    del transactions_df

    #
    # # blocks
    #

    if verbose:
        print()
        print('filtering blocks...')
    blocks_df = etl_load.load_data('blocks', **data_kwargs)

    if verbose:
        print()
        print('saving blocks...')
    blocks_df.to_csv(output_paths['blocks'], index=False)

    if verbose:
        print()
        print('done')


def _determine_latest_missing_extract_range(target_view, source_view):
    exported_raw = etl_list.list_exported_data(
        rowtype='transactions',
        etl_view=source_view,
    )
    exported_view = etl_list.list_exported_data(
        rowtype='transactions',
        etl_view=target_view,
    )

    start_block = exported_view['end_block'] + 1
    end_block = exported_raw['end_block']

    return start_block, end_block


def _summarize_paths(paths, path_ranges, indent=''):
    paths = list(path_ranges.keys())
    print(indent + 'n_paths:', len(paths))
    total_bytes = 0
    for path in paths:
        total_bytes += os.path.getsize(path)
    total_size = humanfriendly.module.format_size(total_bytes)
    print(indent + 'total size:', total_size)


#
# # block timestamps
#


def extract_block_timestamps(start_block=None, end_block=None):
    all_block_timestamps = _load_all_block_timestamps()
    extracted_block_timestamps = etl_load.load_data(
        'blocks',
        start_block=start_block,
        end_block=end_block,
        columns=['number', 'timestamp'],
        etl_view='block_timestamps',
    )
    max_extracted = max(extracted_block_timestamps['number'].values)
    unextracted = {
        k: v for k, v in all_block_timestamps.items() if k > max_extracted
    }
    series = pd.Series(unextracted, name='timestamp')

    # save data
    path = etl_list.get_path(
        exporttype='blocks',
        etl_view='block_timestamps',
        start_block=min(unextracted.keys()),
        end_block=max(unextracted.keys()),
        columns='number,timestamp',
    )
    series.to_csv(path, index_label='number')


def _load_all_block_timestamps(start_block=None, end_block=None):

    block_data = etl_load.load_data(
        'blocks',
        start_block=start_block,
        end_block=end_block,
        # columns=['number', 'timestamp'],
    )
    blocks = block_data['number'].values
    blocks = [int(block) for block in blocks]
    timestamps = [
        int(timestamp) for timestamp in block_data['timestamp'].values
    ]

    return dict(zip(blocks, timestamps))

