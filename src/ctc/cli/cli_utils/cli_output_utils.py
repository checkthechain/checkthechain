from __future__ import annotations

import os
import typing
from ctc import cli

if typing.TYPE_CHECKING:
    from ctc import spec


def print_bullet(
    value: typing.Any,
    *,
    key: typing.Any | None = None,
    number: int | None = None,
    colon_str: str | None = None,
    indent: int | str | None = None,
    bullet_style: str | None = None,
    colon_style: str | None = None,
    key_style: str | None = None,
    value_style: str | None = None,
) -> None:

    import toolstr

    styles = cli.get_cli_styles()

    if bullet_style is None:
        bullet_style = styles['title']
    if colon_style is None:
        colon_style = styles['comment']
    if key_style is None:
        key_style = styles['option']
    if value_style is None:
        value_style = styles['description']

    toolstr.print_bullet(
        key=key,
        value=value,
        number=number,
        colon_str=colon_str,
        indent=indent,
        bullet_style=bullet_style,
        colon_style=colon_style,
        key_style=key_style,
        value_style=value_style,
    )


def output_data(
    data: spec.DataFrame | spec.Series,
    output: str,
    *,
    overwrite: bool,
    top: int | None = None,
    indent: str | int | None = None,
    raw: bool = False,
) -> None:

    if output == 'stdout':
        import toolstr

        if top is not None:
            data = data[:top]
        toolstr.print_dataframe_as_table(data, indent=indent, )

    else:
        import toolcli
        import polars as pl

        # check whether file exists
        if os.path.isfile(output):
            if overwrite:
                pass
            elif toolcli.input_yes_or_no('File already exists. Overwrite? '):
                pass
            else:
                raise Exception('aborting')

        if spec.is_polars_series(data):
            df = pl.DataFrame(data)
        elif spec.is_polars_dataframe(data):
            df = data
        else:
            raise Exception('unknown data format')

        if output.endswith('.parquet'):
            df.write_parquet(output)
        elif output.endswith('.csv'):
            df.write_csv(output)
        elif output.endswith('.json'):
            df.write_json(output)
        else:
            raise Exception('unknown output format: ' + str(output))
