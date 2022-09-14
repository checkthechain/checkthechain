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
) -> None:

    import toolstr

    styles = cli.get_cli_styles()

    toolstr.print_bullet(
        key=key,
        value=value,
        number=number,
        colon_str=colon_str,
        indent=indent,
        bullet_style=styles['title'],
        colon_style=styles['comment'],
        key_style=styles['option'],
        value_style=styles['description'],
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

    import pandas as pd

    if output == 'stdout':
        import toolstr

        rows = []
        if isinstance(data, pd.DataFrame):
            iterator = data.iterrows()
        elif isinstance(data, pd.Series):
            iterator = data.iteritems()
        else:
            raise Exception('unknown data format')

        for index, values in iterator:
            row = []
            row.append(index)
            if hasattr(values, 'values'):
                # dataframe
                for value in values.values:
                    if value and not isinstance(value, str):
                        value = toolstr.format(value)
                    row.append(value)
            else:
                # series
                if raw:
                    row.append(values)
                else:
                    row.append(toolstr.format(values, order_of_magnitude=True))
            rows.append(row)

        if top is not None:
            if len(rows) > top:
                rows = rows[:top]

        if isinstance(data, pd.DataFrame):
            columns = [data.index.name] + list(data.columns)
        elif isinstance(data, pd.Series):
            columns = [data.index.name, data.name]
        else:
            raise Exception('unknown data format')
        toolstr.print_table(rows=rows, labels=columns, indent=indent)

    else:

        import toolcli

        # check whether file exists
        if os.path.isfile(output):
            if overwrite:
                pass
            elif toolcli.input_yes_or_no('File already exists. Overwrite? '):
                pass
            else:
                raise Exception('aborting')

        if output.endswith('.csv'):
            data.to_csv(output)

        elif output.endswith('.json'):
            data.to_json(output)

        else:
            raise Exception('unknown output format: ' + str(output))
