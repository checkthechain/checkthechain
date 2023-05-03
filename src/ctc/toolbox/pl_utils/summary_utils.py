from __future__ import annotations

import typing

import polars as pl

from ctc import spec


def set_column_display_width(width: int = 70) -> None:
    pl.Config.set_fmt_str_lengths(width)


def get_glob_total_bytes(path_template: str) -> int:
    import glob
    import os

    total_size = 0
    for path in glob.glob(path_template):
        total_size += os.path.getsize(path)
    return total_size


def get_series_distribution(series: spec.Series) -> spec.DataFrame:
    dist = (
        series.value_counts()
        .sort('counts', descending=True)
        .rename({'counts': 'count'})
    )
    dist = dist.with_columns(
        pl.col('count').cumsum().alias('cumcount'),
        (pl.col('count') / series.shape[0]).alias('pdf'),
    )
    dist = dist.with_columns(pl.col('pdf').cumsum().alias('cdf'))
    dist.insert_at_idx(1, dist.with_row_count()['row_nr'].alias('rank') + 1)
    return dist


def create_series_summary(series: pl.Series) -> typing.Mapping[str, typing.Any]:
    import toolstr

    if series.dtype == pl.datatypes.Object:
        n_unique = len(set(series.to_list()))
    elif isinstance(series.dtype, pl.List):
        n_unique = len(set(tuple(item) for item in series.to_list()))
    else:
        n_unique = series.n_unique()
    n_rows = len(series)
    n_null = series.is_null().sum()

    # bytes
    n_bytes: int | None = 0
    bytes_per_row = 0
    if series.dtype == pl.datatypes.Int8:
        bytes_per_row = 1
    elif series.dtype == pl.datatypes.Int16:
        bytes_per_row = 2
    elif series.dtype == pl.datatypes.Int32:
        bytes_per_row = 4
    elif series.dtype == pl.datatypes.Int64:
        bytes_per_row = 8
    elif series.dtype == pl.datatypes.Float32:
        bytes_per_row = 4
    elif series.dtype == pl.datatypes.Float64:
        bytes_per_row = 8
    elif series.dtype == pl.datatypes.Utf8:
        bytes_per_row = 8
        str_lengths = series.str.lengths()
        str_lengths_sum = typing.cast(int, str_lengths.sum())
        if str_lengths_sum is not None and n_bytes is not None:
            n_bytes += str_lengths_sum
    elif series.dtype == pl.datatypes.Categorical:
        bytes_per_row = 4
        str_lengths = series.unique().str.lengths()
        str_lengths_sum = typing.cast(int, str_lengths.sum())
        if str_lengths_sum is not None and n_bytes is not None:
            n_bytes += str_lengths_sum
    else:
        n_bytes = None
    if n_bytes is not None:
        n_bytes += bytes_per_row * n_rows

    # human-readable bytes
    if n_bytes is not None:
        h_bytes = toolstr.format_nbytes(n_bytes)
    else:
        h_bytes = None

    # unique compression
    if n_unique < 2**16:
        unique_key_bytes = 2
    elif n_unique < 2**32:
        unique_key_bytes = 4
    else:
        unique_key_bytes = 8
    if series.dtype == pl.datatypes.Utf8:
        unique_lengths = series.unique().str.lengths()
        unique_compress_bytes = (
            unique_key_bytes * n_rows + (unique_key_bytes + 8) * n_unique
        )
        unique_lengths_sum = typing.cast(int, unique_lengths.sum())
        if unique_lengths_sum is not None:
            unique_compress_bytes += unique_lengths_sum
    else:
        unique_compress_bytes = (
            unique_key_bytes + bytes_per_row
        ) * n_unique + unique_key_bytes * n_rows
    if n_bytes is not None and n_bytes != 0:
        unique_compression_factor = unique_compress_bytes / n_bytes
    else:
        unique_compression_factor = None

    # binary compress size
    binary_n_bytes = None
    binary_h_bytes = None
    binary_unique_n_bytes = None
    binary_unique_h_bytes = None
    binary_unique_compression = None
    if series.dtype == pl.datatypes.Utf8:
        try:
            is_hex = True
        except Exception:
            is_hex = False
        if is_hex:
            binary_lengths = (str_lengths - 2) / 2
            binary_n_bytes = 8 * n_rows
            binary_lengths_sum = typing.cast(int, binary_lengths.ceil().sum())
            if binary_lengths_sum is not None:
                binary_n_bytes += binary_lengths_sum
            binary_h_bytes = toolstr.format_nbytes(binary_n_bytes)

            binary_unique_n_bytes = (
                unique_key_bytes * n_rows + (unique_key_bytes + 8) * n_unique
            )
            unique_lengths_sum = typing.cast(
                int, ((unique_lengths - 2) / 2).ceil().sum()
            )
            if unique_lengths_sum is not None:
                binary_unique_n_bytes += unique_lengths_sum

            binary_unique_h_bytes = toolstr.format_nbytes(binary_unique_n_bytes)

            if n_bytes is not None and n_bytes != 0:
                binary_unique_compression = binary_unique_n_bytes / n_bytes
            else:
                binary_unique_compression = None

    return {
        "column": series.name,
        "n_unique": n_unique,
        "%_unique": n_unique / n_rows if n_rows > 0 else None,
        "dtype": str(series.dtype),
        "n_null": n_null,
        "%_null": n_null / n_rows if n_rows > 0 else None,
        "n_bytes": n_bytes,
        "h_bytes": h_bytes,
        'binary_n_bytes': binary_n_bytes,
        'binary_h_bytes': binary_h_bytes,
        "key_size": unique_key_bytes,
        'unique_n_bytes': unique_compress_bytes,
        "unique_h_bytes": toolstr.format_nbytes(unique_compress_bytes),
        'unique_compression': unique_compression_factor,
        'binary_unique_n_bytes': binary_unique_n_bytes,
        'binary_unique_h_bytes': binary_unique_h_bytes,
        'binary_unique_compression': binary_unique_compression,
    }


def create_dataframe_summary(df: spec.DataFrame) -> spec.DataFrame:
    summary = [create_series_summary(df[column]) for column in df.columns]
    return pl.DataFrame(summary)


def print_dataframe_summary(
    df: spec.DataFrame, title: str | None = None
) -> None:
    import toolstr

    summary = create_dataframe_summary(df)

    if title is None:
        title = 'Dataframe Summary'

    toolstr.print_text_box(title)
    non_object_df = df.select(
        column
        for column in df.columns
        if column not in df.select(pl.col(pl.Object))
    )
    rows: typing.Sequence[typing.Sequence[typing.Any]] = [
        ['n_rows', len(df)],
        ['n_columns', len(df.columns)],
        [
            'estimate_bytes()',
            toolstr.format_nbytes(non_object_df.estimated_size()),
        ],
    ]
    toolstr.print_table(rows, indent=4)
    print()

    labels = summary.columns
    column_formats: typing.Mapping[str, typing.Mapping[str, typing.Any]] = {
        "%_unique": {"percentage": True, "decimals": 1},
        "%_null": {"percentage": True, "decimals": 1},
        "unique_compression": {"percentage": True, "decimals": 1},
        'binary_unique_compression': {"percentage": True, "decimals": 1},
    }
    toolstr.print_header('Column summary')
    toolstr.print_dataframe_as_table(
        summary, indent=4, column_formats=column_formats
    )

    print()
    toolstr.print_header('Byte summary')
    n_byte_columns = [
        column for column in df.columns if column.endswith('n_bytes')
    ]
    byte_totals = summary[n_byte_columns].sum()
    rows = [
        [
            name,
            toolstr.format_nbytes(byte_totals[name][0]),
            byte_totals[name][0] / summary["n_bytes"].sum(),
        ]
        for name in byte_totals.columns
    ]
    labels = ["name", "n_bytes", "%"]
    column_formats = {'%': {'percentage': True, 'decimals': 1}}
    toolstr.print_table(
        rows,
        labels=labels,
        column_formats=column_formats,  # type: ignore
        indent=4,
    )

