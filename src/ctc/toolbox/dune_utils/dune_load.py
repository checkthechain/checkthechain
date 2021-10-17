import pandas

from . import dune_paths


def load_dune_data(verbose=True, **filters):
    paths = dune_paths.list_dune_paths(**filters)
    if verbose:
        print('loading paths:')
    dfs = []
    for path in paths:
        if verbose:
            print('    ', path.split(dune_paths.get_dune_root())[-1])
        df = pandas.read_csv(path)
        dfs.append(df)
    df = pandas.concat(dfs)

    if filters['datatype'] == 'events':
        df = df.sort_values(by=['evt_block_number', 'evt_index'])
    else:
        raise Exception('unknown datatype: ' + str(datatype))

    return df

