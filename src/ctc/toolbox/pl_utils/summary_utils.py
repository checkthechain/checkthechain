from __future__ import annotations

import polars as pl


def set_column_display_width(width: int = 70) -> None:
    pl.Config.set_fmt_str_lengths(width)


# def value_counts(df: pl.DataFrame, column: str) -> pl.Series:
#     return df.select(pl.col(column).value_counts(sort=True)).unnest(column)

