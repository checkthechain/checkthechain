from __future__ import annotations

import polars as pl


def set_column_display_width(width: int = 70) -> None:
    pl.Config.set_fmt_str_lengths(width)


def create_series_summary(series):

    import toolstr

    n_unique = series.n_unique()
    n_rows = len(series)
    n_null = series.is_null().sum()

    # bytes
    n_bytes = 0
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
        str_lengths_sum = str_lengths.sum()
        if str_lengths_sum is not None:
            n_bytes += str_lengths_sum
    elif series.dtype == pl.datatypes.Categorical:
        bytes_per_row = 4
        str_lengths = series.unique().str.lengths()
        str_lengths_sum = str_lengths.sum()
        if str_lengths_sum is not None:
            n_bytes += str_lengths.sum()
    else:
        n_bytes = None
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
            unique_key_bytes * n_rows
            + (unique_key_bytes + 8) * n_unique
        )
        unique_lengths_sum = unique_lengths.sum()
        if unique_lengths_sum is not None:
            unique_compress_bytes += unique_lengths_sum
    else:
        unique_compress_bytes = (
            unique_key_bytes + bytes_per_row
        ) * n_unique + unique_key_bytes * n_rows
    unique_compression_factor = unique_compress_bytes / n_bytes

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
            binary_lengths_sum = binary_lengths.ceil().sum()
            if binary_lengths_sum is not None:
                binary_n_bytes += binary_lengths_sum
            binary_h_bytes = toolstr.format_nbytes(binary_n_bytes)

            binary_unique_n_bytes = (
                unique_key_bytes * n_rows
                + (unique_key_bytes + 8) * n_unique
            )
            unique_lengths_sum = ((unique_lengths - 2) / 2).ceil().sum()
            if unique_lengths_sum is not None:
                binary_unique_n_bytes += unique_lengths_sum

            binary_unique_h_bytes = toolstr.format_nbytes(binary_unique_n_bytes)
            binary_unique_compression = binary_unique_n_bytes / n_bytes

    return {
        "column": series.name,
        "n_unique": n_unique,
        "%_unique": n_unique / n_rows,
        "dtype": series.dtype.string_repr(),
        "n_null": n_null,
        "%_null": n_null / n_rows,
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


def create_dataframe_summary(df: pl.DataFrame) -> pl.DataFrame:
    summary = [create_series_summary(df[column]) for column in df.columns]
    return pl.DataFrame(summary)


def print_dataframe_summary(df: pl.DataFrame) -> pl.DataFrame:

    import toolstr

    summary = create_dataframe_summary(df)

    toolstr.print_text_box('Dataframe summary')
    rows = [
        ['n_rows', len(df)],
        ['n_columns', len(df.columns)],
        ['estimate_bytes()', toolstr.format_nbytes(df.estimated_size())],
    ]
    toolstr.print_table(rows, indent=4)
    print()

    labels = summary.columns
    column_formats = {
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
        rows, labels=labels, column_formats=column_formats, indent=4
    )

