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

        return yaml.load(f, Loader=yaml.CLoader)
    else:
        raise Exception('unknown file type: ' + str(path))

