import os
import typing

import toolcache


@toolcache.cache(cachetype='memory')
def load_file_data(path: str) -> typing.Any:
    if path.endswith('.json'):
        import json

        with open(path, 'r') as f:
            return json.load(f)
    elif path.endswith('.ast'):
        import ast

        with open(path, 'r') as f:
            return ast.literal_eval(f.read())
    elif path.endswith('.csv'):
        import pandas as pd

        df = pd.read_csv(path)
        return df.to_dict(orient='records')
    elif path.endswith('.yaml'):
        import yaml

        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif path.endswith('.toml'):
        import toml

        with open(path, 'r') as f:
            return toml.load(f)
    else:
        raise Exception('unknown file type: ' + str(path))


def write_file_data(
    path: str,
    data: typing.Union[list[dict], dict[typing.Any, dict]],
    overwrite: bool = False,
    index_field: typing.Optional[str] = None,
) -> None:

    if os.path.isfile(path) and not overwrite:
        raise Exception('file already exists, use overwrite=True')

    if index_field is not None:
        if not isinstance(data, dict):
            raise Exception('index_field is used to convert dict -> list')
        data = [
            dict(datum, **{index_field: index}) for index, datum in data.items()
        ]

    if path.endswith('.json'):
        import json

        with open(path, 'w') as f:
            json.dump(data, f)
    elif path.endswith('.ast'):
        with open(path, 'w') as f:
            f.write(str(data))
    elif path.endswith('.toml'):
        import toml

        if isinstance(data, list):
            raise Exception('can only write mappings to toml, not sequences')

        with open(path, 'w') as f:
            toml.dump(data, f)
    elif path.endswith('.yaml'):
        import yaml

        with open(path, 'w') as f:
            yaml.dump(data, f)
    elif path.endswith('.csv'):
        import csv

        # gather fields
        field_set: set[str] = set()
        if isinstance(data, list):
            dataiter: typing.Iterable[dict] = data
        elif isinstance(data, dict):
            dataiter = data.values()
        else:
            raise Exception('unknown data type: ' + str(type(data)))
        field_set = {key for datum in dataiter for key in datum.keys()}
        fields = sorted(field_set)

        with open(path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
    else:
        raise Exception('unknown file type: ' + str(path))

