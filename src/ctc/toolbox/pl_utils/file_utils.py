from __future__ import annotations

import os
import typing

import polars as pl


def create_multipath_glob(paths: typing.Sequence[str]) -> str:
    """create a glob that points to a specific set of files

    works by creating a temporary directory filled with symlinks, so epheremeral
    """
    import tempfile

    temp_dir = tempfile.mkdtemp()
    for path in paths:
        os.symlink(path, os.path.join(os.path.basename(path)))
    return os.path.join(temp_dir, '*')


def write_df(
    df: pl.DataFrame,
    path: str,
    *,
    n_row_groups: int | None = None,
    row_group_size: int | None = None,
    **write_kwargs: typing.Any,
) -> None:
    import shutil

    if n_row_groups is not None:
        write_kwargs['row_group_size'] = int(len(df) / n_row_groups)
    elif row_group_size is not None:
        write_kwargs['row_group_size'] = row_group_size

    temp_path = path + '_temp'
    if path.endswith('.parquet'):
        df.write_parquet(temp_path, **write_kwargs)
    elif path.endswith('.csv'):
        df.write_csv(temp_path, **write_kwargs)
    else:
        raise Exception('unknown file format: ' + str(path))

    shutil.move(temp_path, path)


# def add_stats_to_parquet_file(
#     path: str,
#     *,
#     new_path: str | None = None,
#     replace: bool = False,
# ):
#     if new_path is None:
#         if replace:
#             new_path = path + '_tmp'
#         else:
#             pass

#     df = pl.read_parquet(path)
#     df.write_parquet(new_path, statistics=True)

#     if replace:
#         shutil.move(new_path, path)

