from __future__ import annotations

import typing

import polars as pl

from ctc import spec


def prefix_hex_series_to_binary(series: pl.Series) -> pl.Series:
    return series.str.slice(2).apply(
        bytes.fromhex,
        return_dtype=pl.datatypes.Binary,
    )


def raw_hex_series_to_binary(series: pl.Series) -> pl.Series:
    return series.apply(bytes.fromhex, return_dtype=pl.datatypes.Binary)


def binary_series_to_prefix_hex(series: pl.Series) -> pl.Series:
    return '0x' + binary_series_to_raw_hex(series)


def binary_series_to_raw_hex(series: pl.Series) -> pl.Series:
    as_hex = [(x.hex() if x is not None else None) for x in series.to_list()]
    return pl.Series(series.name, as_hex, pl.datatypes.Utf8)


def binary_columns_to_prefix_hex(
    df: spec.DataFrame, columns: typing.Sequence[str] | None = None
) -> spec.DataFrame:
    if columns is None:
        columns = df.select(pl.col(pl.datatypes.Binary)).columns
    return df.with_columns(
        [binary_series_to_prefix_hex(df[column]) for column in columns]
    )


def binary_columns_to_raw_hex(
    df: spec.DataFrame, columns: typing.Sequence[str] | None = None
) -> spec.DataFrame:
    if columns is None:
        columns = df.select(pl.col(pl.datatypes.Binary)).columns
    return df.with_columns(
        [binary_series_to_raw_hex(df[column]) for column in columns]
    )


def prefix_hex_columns_to_binary(
    df: spec.DataFrame, columns: typing.Sequence[str] | None = None
) -> spec.DataFrame:
    if columns is None:
        columns = []
        for column, dtype in zip(df.columns, df.dtypes):
            if dtype == pl.datatypes.Utf8:
                try:
                    bytes.fromhex(df[column][0][2:])
                    columns.append(column)
                except Exception:
                    continue
    return df.with_columns(
        [prefix_hex_series_to_binary(df[column]) for column in columns]
    )


def raw_hex_columns_to_binary(
    df: spec.DataFrame, columns: typing.Sequence[str] | None = None
) -> spec.DataFrame:
    if columns is None:
        columns = []
        for column, dtype in zip(df.columns, df.dtypes):
            if dtype == pl.datatypes.Utf8:
                try:
                    bytes.fromhex(df[column][0])
                    columns.append(column)
                except Exception:
                    continue
    return df.with_columns(
        [raw_hex_series_to_binary(df[column]) for column in columns]
    )

