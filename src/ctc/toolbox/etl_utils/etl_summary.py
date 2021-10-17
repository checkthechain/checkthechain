import numpy as np

from . import etl_list


def summarize_etl_data(rowtype, etl_view):

    exported_data = etl_list.list_exported_data(rowtype, etl_view)
    path_ranges = exported_data['path_ranges']
    all_bounds = [
        bound
        for block_range in exported_data['path_ranges'].values()
        for bound in block_range
    ]
    min_block = min(all_bounds)
    max_block = max(all_bounds)
    block_index = list(range(min_block, max_block + 1))
    block_counts = np.zeros(max_block - min_block + 1)

    chunk_sizes = set()
    for path, (path_start_block, path_end_block) in path_ranges.items():
        start_index = block_index.index(path_start_block)
        end_index = block_index.index(path_end_block) + 1
        block_counts[start_index:end_index] += 1
        chunk_sizes.add(path_end_block - path_start_block + 1)

    n_missing_blocks = (block_counts == 0).sum()
    overlapping_ranges = (block_counts > 1).sum() > 0
    if n_missing_blocks == 0:
        n_missing_chunks = 0
    elif len(chunk_sizes) == 1:
        n_missing_chunks = n_missing_blocks / list(chunk_sizes)[0]
        if n_missing_chunks == int(n_missing_chunks):
            n_missing_chunks = int(n_missing_chunks)
    else:
        n_missing_chunks = '[multiple chunk sizes]'

    print('# Summary of', rowtype)
    print('- blocks:')
    print('    - block_range: [' + str(min_block) + ', ' + str(max_block) + ']')
    print('    - n_missing_blocks:', n_missing_blocks)
    print('- chunks:')
    print('    - overlapping_ranges:', overlapping_ranges)
    print('    - n_chunks:', len(exported_data['path_ranges']))
    print('    - n_missing_chunks:', n_missing_chunks)
    print('    - chunk_sizes:', ', '.join(str(chunk) for chunk in chunk_sizes))

