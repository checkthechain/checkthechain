import numpy as np
import pandas as pd

from ctc import config_utils

from . import etl_list
from . import etl_spec


def load_data(
    rowtype,
    start_block=None,
    end_block=None,
    etl_backend=None,
    etl_view=None,
    columns=None,
):

    if etl_backend is None:
        etl_backend = config_utils.get_config()['etl_backend']
    if start_block is None or end_block is None:
        exported_data = etl_list.list_exported_data(
            rowtype,
            etl_view=etl_view,
            etl_backend=etl_backend,
            columns=columns,
        )
        if start_block is None:
            start_block = exported_data['start_block']
        if end_block is None:
            end_block = exported_data['end_block']

    kwargs = {
        'rowtype': rowtype,
        'start_block': start_block,
        'end_block': end_block,
        'columns': columns,
    }

    if etl_backend in ['filesystem', 's3']:
        return _load_data_from_chunks(
            etl_backend=etl_backend,
            etl_view=etl_view,
            exported_columns=columns,
            **kwargs
        )
    elif etl_backend == 'sql':
        return _load_data_sql(**kwargs)
    else:
        raise Exception('unknown data etl_backend: ' + str(etl_backend))


def _load_data_from_chunks(
    rowtype,
    start_block,
    end_block,
    etl_view,
    exported_columns=None,
    columns=None,
    etl_chunk_root=None,
    etl_backend=None,
):
    if etl_view is None:
        etl_view = 'raw'

    block_number_column = etl_spec.block_number_columns[rowtype]

    exported_data = etl_list.list_exported_data(
        rowtype=rowtype,
        start_block=start_block,
        end_block=end_block,
        columns=exported_columns,
        etl_chunk_root=etl_chunk_root,
        etl_backend=etl_backend,
        etl_view=etl_view,
    )
    path_ranges = exported_data['path_ranges']

    if start_block is None or end_block is None:
        start_blocks = []
        end_blocks = []
        for start_block, end_block in exported_data['path_ranges'].values():
            start_blocks.append(start_block)
            end_blocks.append(end_block)
        start_block = min(start_blocks)
        end_block = max(start_blocks)

    loaded_index = list(range(start_block, end_block + 1))
    loaded_mask = np.zeros(end_block - start_block + 1, dtype=int)
    dfs = []
    for path, (path_start_block, path_end_block) in path_ranges.items():
        block_slice = etl_list.get_block_slice(
            path_start_block, path_end_block, loaded_index
        )
        if np.any(loaded_mask[block_slice] == 0):
            path_df = _load_chunk(path=path, columns=columns)
            path_df = path_df[path_df[block_number_column] >= start_block]
            path_df = path_df[path_df[block_number_column] <= end_block]
            dfs.append(path_df)
            loaded_mask[block_slice] += 1

    # if it is possible to have overlapping data, take unique rows only
    overlapping_ranges = (loaded_mask > 1).sum() > 0
    if overlapping_ranges:
        raise NotImplementedError()

    # ensure that entire block range is loaded
    if np.any(loaded_mask == 0):
        missing_blocks = np.nonzero(~loaded_mask)[0]
        raise Exception('missing ' + str(len(missing_blocks)) + ' blocks')

    # concatenate pieces together
    df = pd.concat(dfs, sort=False, ignore_index=True)
    df = df.sort_values(by=block_number_column)
    df = df.reset_index(drop=True)

    return df


def _load_chunk(path, columns=None):
    if path.startswith('s3://'):
        raise NotImplementedError()
    else:
        return pd.read_csv(path, index_col=False, usecols=columns)


def _load_data_sql():
    raise NotImplementedError()

