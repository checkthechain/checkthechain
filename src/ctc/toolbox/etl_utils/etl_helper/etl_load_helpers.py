from .. import etl_load


def load_block_timestamps(start_block=None, end_block=None):

    return etl_load.load_data(
        rowtype='blocks',
        etl_view='block_timestamps',
        columns=['number', 'timestamp'],
        start_block=start_block,
        end_block=end_block,
    ).set_index('number')['timestamp'].to_dict()
