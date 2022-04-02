from __future__ import annotations

import toolsql

from ctc import config


def create_engine(datatype, network=None):

    # get db config
    data_source = config.get_data_source(datatype=datatype, network=network)
    if data_source['backend'] == 'hybrid':
        data_source = data_source['hybrid_order'][0]
    if data_source.get('backend') != 'db' or 'db_config' not in data_source:
        raise Exception('not using database for this type of data')
    db_config = data_source['db_config']

    # create engine
    return toolsql.create_engine(db_config=db_config)

