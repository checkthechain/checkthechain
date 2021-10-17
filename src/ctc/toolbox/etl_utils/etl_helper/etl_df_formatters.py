import decimal

import pandas as pd

from ctc import directory


def format_raw_dataframe(
    dataframe,
    format_columns=None,
    convert_to_type=None,
    rescale=None,
    rescale_factor=None,
    token_symbol=None,
):

    # parse inputs
    if format_columns is None:
        format_columns = ['value']
    if isinstance(convert_to_type, str):
        if convert_to_type == 'float':
            convert_to_type = float
        elif convert_to_type == 'decimal':
            convert_to_type = decimal.Decimal
        elif convert_to_type == 'int':
            convert_to_type = int
    if rescale is None:
        rescale = rescale_factor is not None
    if rescale and rescale_factor is None:
        if token_symbol is None:
            raise Exception('to rescale specify rescale_factor or token_symbol')
        rescale_factor = directory.get_token_n_decimals(
            token_symbol=token_symbol
        )
        n_decimals = directory.get_token_n_decimals(token_symbol=token_symbol)
        rescale_factor = decimal.Decimal('10e' + str(int(n_decimals - 1)))

    # format dataframe
    for column in format_columns:
        if column in dataframe:
            if convert_to_type:
                dataframe[column] = dataframe[column].map(convert_to_type)
            if rescale:
                if len(dataframe) > 0:
                    column_type = type(dataframe[column].values[0])
                    typed_rescale_factor = column_type(rescale_factor)
                    dataframe[column] = dataframe[column] / typed_rescale_factor


def format_log_dataframe(dataframe):

    # split log topics into multiple columns
    log_topics = dataframe['topics'].str.split(',', expand=True)
    log_topics.columns = ['topic' + str(t) for t in range(4)]
    formatted_logs = pd.concat([dataframe, log_topics], axis='columns')
    del formatted_logs['topics']

    # reindex with multilevel index
    formatted_logs = formatted_logs.set_index(
        ['block_number', 'transaction_index', 'log_index']
    )
    formatted_logs = formatted_logs.sort_index()

    formatted_logs = formatted_logs.rename(
        columns={'address': 'contract_address'}
    )

    return formatted_logs

