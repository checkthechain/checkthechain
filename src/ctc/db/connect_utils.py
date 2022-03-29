import toolsql

from ctc import config


def create_engine(datatype):

    # get db config
    data_source = config.get_data_source(datatype)
    if data_source.get('backend') != 'db' or 'db_config' in data_source:
        raise Exception('not using database for this type of data')
    db_config = data_source['db_config']

    # create engine
    return toolsql.create_engine(db_config=db_config)

