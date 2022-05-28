from __future__ import annotations

import typing
import toolsql

from ctc import config
from ctc import spec

from . import schema_utils


def create_engine(
    schema_name: schema_utils.SchemaName,
    network: spec.NetworkReference,
) -> toolsql.SAEngine | None:
    """create sqlalchemy engine object"""

    # get db config
    data_source: config.DataSource | config.LeafDataSource = (
        config.get_data_source(datatype=schema_name, network=network)
    )
    if data_source['backend'] == 'hybrid':
        data_source = typing.cast(config.DataSource, data_source)[
            'hybrid_order'
        ][0]
    if data_source.get('backend') != 'db' or 'db_config' not in data_source:
        raise Exception('not using database for this type of data')
    db_config = data_source['db_config']
    if db_config is None:
        raise Exception('invalid db_config')

    # create engine
    return toolsql.create_engine(db_config=db_config)
