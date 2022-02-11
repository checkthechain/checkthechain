import os
import typing
from typing_extensions import Literal

import toolcache


formats = ['json', 'ast', 'csv', 'yaml', 'toml']
DataFormat = Literal['json', 'ast', 'csv', 'yaml', 'toml']


def get_path_data_format(path: str) -> DataFormat:

    extension = os.path.splitext(path)[-1]
    extension = extension[1:]

    # python3.7 compatibility
    # args = typing.get_args(DataFormat)
    args = DataFormat.__args__  # type: ignore

    if extension in args:
        return typing.cast(DataFormat, extension)
    else:
        raise Exception('unknown file type: ' + str(extension))


@toolcache.cache(cachetype='memory')
def load_file_data(
    path: str, format: typing.Optional[DataFormat] = None
) -> typing.Any:

    if format is None:
        format = get_path_data_format(path=path)
    with open(path, 'r') as f:
        return load_buffer_data(buffer=f, format=format)


def load_buffer_data(buffer: typing.TextIO, format: DataFormat) -> typing.Any:
    if format == 'json':
        import json

        return json.load(buffer)
    elif format == 'ast':
        import ast

        return ast.literal_eval(buffer.read())
    elif format == 'csv':
        import pandas as pd

        df = pd.read_csv(buffer)
        return df.to_dict(orient='records')
    elif format == 'yaml':
        import yaml

        return yaml.safe_load(buffer)
    elif format == 'toml':
        import toml

        return toml.load(buffer)
    else:
        raise Exception('unknown format: ' + str(format))


def write_file_data(
    path: str,
    data: typing.Union[
        typing.Sequence[typing.Mapping],
        typing.Mapping[typing.Any, typing.Mapping],
    ],
    format: typing.Optional[DataFormat] = None,
    overwrite: bool = False,
    index_field: typing.Optional[str] = None,
) -> None:

    if format is None:
        format = get_path_data_format(path=path)

    if os.path.isfile(path) and not overwrite:
        raise Exception('file already exists, use overwrite=True')

    with open(path, 'w') as f:
        write_buffer_data(
            buffer=f,
            data=data,
            index_field=index_field,
            format=format,
        )


def write_buffer_data(
    buffer: typing.TextIO,
    data: typing.Union[
        typing.Sequence[typing.Mapping],
        typing.Mapping[typing.Any, typing.Mapping],
    ],
    format: DataFormat,
    index_field: typing.Optional[str] = None,
) -> None:

    if index_field is not None:
        if not isinstance(data, dict):
            raise Exception('index_field is used to convert dict -> list')
        data = [
            dict(datum, **{index_field: index}) for index, datum in data.items()
        ]

    if format == 'json':
        import json

        json.dump(data, buffer)
    elif format == 'ast':
        buffer.write(str(data))
    elif format == 'toml':
        import toml

        if not isinstance(data, typing.Mapping):
            raise Exception('can only write mappings to toml, not sequences')

        toml.dump(data, buffer)
    elif format == 'yaml':
        import yaml

        yaml.dump(data, buffer)
    elif format == 'csv':
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

        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    else:
        raise Exception('unknown format: ' + str(format))

