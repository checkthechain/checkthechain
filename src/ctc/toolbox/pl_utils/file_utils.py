from __future__ import annotations

import typing

import os


def create_multipath_glob(paths: typing.Sequence[str]) -> str:
    """create a glob that points to a specific set of files

    works by creating a temporary directory filled with symlinks, so epheremeral
    """
    import tempfile

    temp_dir = tempfile.mkdtemp()
    for path in paths:
        os.symlink(path, os.path.join(os.path.basename(path)))
    return os.path.join(temp_dir, '*')


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
