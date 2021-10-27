"""

- maybe

"""
import eth_abi
import pandas as pd

from .. import binary_utils
from . import event_parsing


def encode_event_topics():
    raise NotImplementedError()


def encode_event_data(data, unindexed_types=None, output_format=None):
    raise NotImplementedError()


def decode_event_topics(
    topics, indexed_types=None, indexed_names=None, use_names=True, **abi_query
):
    """


    remaining edgecase:
    - variable data in indexed topic?
    """

    # get abi
    if indexed_types is None:
        indexed_types = event_parsing.get_event_indexed_types(**abi_query)

    # decode
    decoded_topics = []
    for topic, indexed_type in zip(topics[1:], indexed_types):
        decoded_topic = eth_abi.decode_single(indexed_type, topic)
        decoded_topics.append(decoded_topic)

    # package output
    if not use_names:
        return decoded_topics
    else:
        if indexed_names is None:
            indexed_names = event_parsing.get_event_indexed_names(**abi_query)
        return dict(zip(indexed_names, decoded_topics))


def decode_event_data(
    data,
    unindexed_types=None,
    unindexed_names=None,
    use_names=True,
    **abi_query
):
    """decode the unindexed data of event"""

    # gather metadata
    if unindexed_types is None:
        unindexed_types = event_parsing.get_event_unindexed_types(**abi_query)

    # decode data
    data = binary_utils.convert_format(data, 'binary')
    decoded = eth_abi.decode_single(unindexed_types, data)

    # package outputs
    if not use_names:
        return decoded
    else:
        if unindexed_names is None:
            unindexed_names = event_parsing.get_event_unindexed_names(
                **abi_query
            )
        return dict(zip(unindexed_names, decoded))


#
# # dataframes
#


def decode_events_dataframe(
    df, event_abi=None, delete_data_column=True, **abi_query
):
    """decode dataframe that contains raw event data

    ## Replaces Columns
    - topic0
    - topic1
    - topic2
    - topic3

    ## Removes Columns
    - data

    ## Adds Columns
    - arg__<name>
    """

    raise Exception('need to figure out if this could be rewritten better')

    if event_abi is None:
        event_abi = event_parsing.get_event_abi(**abi_query)

    # validate data
    if len(df) > 0:

        # assert only one event type used
        assert len(set(df['topic0'])) == 1

        # assert event hash matches event_abi
        assert df['topic0'].iloc[0] == event_parsing.get_event_hash(
            event_abi=event_abi
        )

    # decode data items
    unindexed_types = event_parsing.get_event_unindexed_types(
        event_abi=event_abi
    )
    unindexed_names = event_parsing.get_event_unindexed_names(
        event_abi=event_abi
    )
    for name in unindexed_names:
        if name in df.columns:
            raise Exception('column name collision')
    decoded = {name: {} for name in unindexed_names}
    for index, value in df['data'].items():
        decoded_data = decode_event_data(
            data=value,
            unindexed_types=unindexed_types,
            unindexed_names=unindexed_names,
        )
        for name, subvalue in decoded_data.items():
            decoded[name][index] = subvalue

    # concatenate
    new_df = pd.concat([df, pd.DataFrame(decoded)], axis=1)
    new_df = new_df.reindex(df.index)
    if delete_data_column:
        del new_df['data']

    # rename topic0 to event_type
    if 'event_type' in new_df:
        raise Exception('column name collision')
    new_df = new_df.rename(columns={'topic0': 'event_type'})

    # decode other topics
    # need to double check this section
    indexed_types = event_parsing.get_event_indexed_types(event_abi=event_abi)
    for t, indexed_type in enumerate(indexed_types):
        if indexed_type == 'address':
            topic = 'topic' + str(t + 1)
            new_df[topic] = '0x' + new_df[topic].str[26:]

    # rename topicX to indexed variable names
    indexed_names = event_parsing.get_event_indexed_names(event_abi=event_abi)
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

