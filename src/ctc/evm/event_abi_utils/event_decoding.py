import ethereum.abi
import pandas as pd

from . import event_querying


def decode_event_data(data, event_data_types=None, **abi_kwargs):
    """decode data for a single event"""

    if event_data_types is None:
        event_data_types = event_querying.get_event_data_types(**abi_kwargs)

    return ethereum.abi.decode_abi(
        types=event_data_types,
        data=bytes.fromhex(data[2:]),
    )


def decode_events(df, event_abi, delete_coded_column=True):
    """decode events for a dataframe that contains a single event type

    df should be a dataframe of events with specific columns:
    - topic0: the event type
    - data: the unindexed event data
    """

    if len(df) > 0:
        assert len(set(df['topic0'])) == 1
        assert df['topic0'].iloc[0] == event_querying.get_event_hash(
            event_abi=event_abi
        )

    # decode data items
    event_data_types = event_querying.get_event_data_types(event_abi=event_abi)
    event_data_names = event_querying.get_event_data_names(event_abi=event_abi)
    for name in event_data_names:
        if name in df.columns:
            raise Exception('column name collision')
    decoded = {name: {} for name in event_data_names}
    for index, value in df['data'].items():
        decoded_data = decode_event_data(
            data=value, event_data_types=event_data_types
        )
        for name, subvalue in zip(event_data_names, decoded_data):
            decoded[name][index] = subvalue

    # concatenate
    new_df = pd.concat([df, pd.DataFrame(decoded)], axis=1)
    new_df = new_df.reindex(df.index)
    if delete_coded_column:
        del new_df['data']

    # rename topic0 to event_type
    if 'event_type' in new_df:
        raise Exception('column name collision')
    new_df = new_df.rename(columns={'topic0': 'event_type'})

    # decode indexed topic inputs
    indexed_types = event_querying.get_event_indexed_types(event_abi=event_abi)
    for t, indexed_type in enumerate(indexed_types):
        if indexed_type == 'address':
            topic = 'topic' + str(t + 1)
            new_df[topic] = '0x' + new_df[topic].str[26:]

    # rename topicX to indexed variable names
    indexed_names = event_querying.get_event_indexed_names(event_abi=event_abi)
    indexed_rename = {
        'topic' + str(i + 1): name for i, name in enumerate(indexed_names)
    }
    for name in indexed_names:
        if name in new_df.columns:
            raise Exception('column name collision')
    new_df = new_df.rename(columns=indexed_rename)
    if len(indexed_names) == 1:
        del new_df['topic2']
        del new_df['topic3']
    elif len(indexed_names) == 2:
        del new_df['topic3']

    return new_df

