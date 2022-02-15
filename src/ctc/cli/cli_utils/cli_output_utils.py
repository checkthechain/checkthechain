import os

import toolcli


def output_data(data, output, overwrite, top=None, indent=None, raw=False):

    import pandas as pd

    if output == 'stdout':
        # print(data)
        import tooltable
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
        tooltable.print_table(rows=rows, headers=columns, indent=indent)

    else:

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

