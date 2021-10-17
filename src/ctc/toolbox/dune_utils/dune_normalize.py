import os

import pandas

from . import dune_paths


def normalize_dune_download(path):
    print('normalizing dune download:', path)
    df = pandas.read_csv(path)
    normalized_df = normalize_dune_data(df)
    normalized_path = get_normalized_dune_path(path, df)
    os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
    normalized_df.to_csv(normalized_path, index=False)
    print('saving to new path:', normalized_path)


def get_normalized_dune_path(old_path, df):

    # parse name
    old_filename = os.path.basename(old_path)
    name = os.path.splitext(old_filename)[0]
    project, datatype = name.split('.')

    if '_evt_' in datatype:

        # parse metadata
        contract, event_name = datatype.split('_evt_')
        start_block = df['evt_block_number'].min()
        end_block = df['evt_block_number'].max()

        return dune_paths.get_dune_path(
            dune_view='normalized',
            project=project,
            contract=contract,
            event_name=event_name,
            start_block=start_block,
            end_block=end_block,
        )

    else:
        raise Exception('unknown path type:')


def normalize_dune_data(df):
    for hash_column in _infer_hash_columns(df):
        df[hash_column] = df[hash_column].apply(replace_dune_hash)

    return df


def _infer_hash_columns(df):
    return [
        column_name
        for column_name, column_value in df.iloc[0].iteritems()
        if isinstance(column_value, str) and column_value.startswith('\\x')
    ]


def replace_dune_hash(dune_hash):
    return '0' + dune_hash[1:]

