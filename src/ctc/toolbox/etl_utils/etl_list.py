"""
in future if this code needs to scale to millions of files, can
- cache intermediate path parsing values
- eliminate column specification
"""

import os

import numpy as np

from ctc import config_utils
from . import etl_spec


def get_default_etl_chunk_root(etl_backend=None):
    config = config_utils.get_config()

    # get chunk storage
    if etl_backend is None:
        etl_backend = config['etl_backend']

    # get chunk root
    if etl_backend == 'filesystem':
        return config['etl_root']
    elif etl_backend == 's3':
        return config['etl_chunk_root_s3']
    else:
        raise Exception('unknown etl_backend: ' + str(etl_backend))


#
# # listing functions
#


def list_exported_data(
    rowtype,
    etl_view,
    start_block=None,
    end_block=None,
    include_path_ranges=None,
    columns=None,
    etl_chunk_root=None,
    etl_backend=None,
):
    """

    - start_block: int lowest block to include in index
    - end_block: int highest block to include in index
    - include_path_ranges: specify included paths according to their block range
        - 'all': include all paths
        - 'contained': include paths whose ranges are contained in given range
        - 'overlapping': include paths whose ranges overlap with given range
    """

    paths = list_chunk_paths(
        etl_view=etl_view,
        etl_chunk_root=etl_chunk_root,
        etl_backend=etl_backend,
        rowtype=rowtype,
    )

    if include_path_ranges is None:
        include_path_ranges = 'overlapping'
    if start_block is None or end_block is None:
        min_start_block, max_end_block = _get_max_block_range(paths)
        if start_block is None:
            start_block = min_start_block
        if end_block is None:
            end_block = max_end_block

    n_block_counts = end_block - start_block + 1
    mask_index = list(range(start_block, end_block + 1))
    if columns is None:
        columns = ''
    if not isinstance(columns, str):
        columns = ','.join(columns)

    # allocate outputs
    path_ranges = {}
    block_counts = np.zeros(n_block_counts, dtype=int)

    # parse existing paths
    for path in paths:

        # parse start and end block
        path_start_block, path_end_block = get_path_block_range(path)

        # skip if path columns do not match input columns
        if columns != _get_path_columns(path):
            continue

        # skip if outside of included block range
        if include_path_ranges == 'all':
            pass
        elif include_path_ranges == 'contained':
            if not (
                start_block <= path_start_block and path_end_block <= end_block
            ):
                continue
        elif include_path_ranges == 'overlapping':
            if not (
                (start_block <= path_end_block)
                and (path_start_block <= end_block)
            ):
                continue
        else:
            raise Exception('unknown include_path_ranges')

        # compile included blocks
        path_ranges[path] = [path_start_block, path_end_block]
        if start_block <= path_start_block and path_end_block <= end_block:
            block_slice = get_block_slice(
                path_start_block, path_end_block, mask_index
            )
            block_counts[block_slice] += 1

    return {
        'start_block': mask_index[0],
        'end_block': mask_index[-1],
        'mask_index': mask_index,
        'block_counts': block_counts,
        'path_ranges': path_ranges,
    }


def list_chunk_paths(
    rowtype, etl_view=None, etl_chunk_root=None, etl_backend=None, sort=True
):
    """list exported chunk paths"""

    if etl_view is None:
        etl_view = 'raw'
    if etl_chunk_root is None:
        etl_chunk_root = get_default_etl_chunk_root(etl_backend=etl_backend)

    kwargs = {
        'etl_chunk_root': etl_chunk_root,
        'etl_view': etl_view,
        'rowtype': rowtype,
    }
    if etl_chunk_root.startswith('s3://'):
        paths = _list_chunk_paths_s3(**kwargs)
    else:
        paths = _list_chunk_paths_filesystem(**kwargs)

    if sort:
        paths = sorted(paths)

    return paths


def get_path_block_range(path):
    """get smallest block range that contains block ranges of all paths"""
    filename = os.path.basename(path)
    pieces = filename.split('__')
    for piece in pieces:
        if '_to_' in piece:
            break
    else:
        raise Exception('could not parse block range from path')
    start_block, _, end_block = piece.split('_')
    start_block = int(start_block)
    end_block = int(end_block)
    return start_block, end_block


def get_block_slice(start_block, end_block, block_index):
    """get a slice() object that selects a block range according to an index"""

    index_start = block_index[0]
    index_end = block_index[-1]

    if index_start <= start_block and start_block <= index_end:
        start_index = block_index.index(start_block)
    else:
        start_index = 0

    if index_start <= end_block and end_block <= index_end:
        end_index = block_index.index(end_block) + 1
    else:
        end_index = len(block_index)

    return slice(start_index, end_index)


def get_path(exporttype, etl_chunk_root=None, etl_backend=None, **kwargs):
    kwargs.setdefault('columns', '')
    if etl_chunk_root is None:
        etl_chunk_root = get_default_etl_chunk_root(etl_backend=etl_backend)
    filename = etl_spec.path_templates[exporttype].format(**kwargs)

    path = os.path.join(etl_chunk_root, filename)

    return path


#
# # helper functions
#


def _get_max_block_range(paths):
    min_start_block = float('inf')
    max_end_block = float('-inf')
    for path in paths:
        start_block, end_block = get_path_block_range(path)
        if start_block < min_start_block:
            min_start_block = start_block
        if end_block > max_end_block:
            max_end_block = end_block
    return min_start_block, max_end_block


def _get_path_columns(path):
    filename = os.path.basename(os.path.splitext(path)[0])
    pieces = filename.split('__')
    columns_piece = pieces[-1]
    return columns_piece


def _list_chunk_paths_filesystem(etl_chunk_root, etl_view, rowtype):
    rowdir = os.path.join(etl_chunk_root, etl_view, rowtype)
    files = os.listdir(rowdir)
    return [os.path.join(rowdir, file) for file in files]


def _list_chunk_paths_s3(etl_chunk_root, rowtype):
    # see https://stackoverflow.com/a/3345727
    raise NotImplementedError()

