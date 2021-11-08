"""

- maybe

"""
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
        topic = binary_utils.convert_binary_format(topic, 'binary')
        decoded_topic = binary_utils.decode_evm_data(indexed_type, topic)
        decoded_topics.append(decoded_topic)

    # package output
    if not use_names:
        return decoded_topics
    else:
        if indexed_names is None:
            indexed_names = event_parsing.get_event_indexed_names(**abi_query)
        return dict(zip(indexed_names, decoded_topics))


def decode_event_unindexed_data(
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
    data = binary_utils.convert_binary_format(data, 'binary')
    decoded = binary_utils.decode_evm_data('(' + ','.join(unindexed_types) + ')', data)

    # package outputs
    if not use_names:
        return decoded
    else:
        if unindexed_names is None:
            unindexed_names = event_parsing.get_event_unindexed_names(
                **abi_query
            )
        return dict(zip(unindexed_names, decoded))


def normalize_event(event, arg_prefix='arg__', **abi_query):

    if abi_query.get('contract_address') is None:
        abi_query['contract_address'] = event['address']
    if abi_query.get('event_hash') is None:
        abi_query['event_hash'] = event['topics'][0]
    if abi_query.get('event_name') is None:
        event_abi = event_parsing.get_event_abi(**abi_query)
        abi_query['event_name'] = event_abi['name']

    # decode event args
    decoded_topics = decode_event_topics(topics=event['topics'], **abi_query)
    decoded_data = decode_event_unindexed_data(data=event['data'], **abi_query)

    # remove keys
    remove_keys = ['data', 'topics', 'removed']
    event = {k: v for k, v in event.items() if k not in remove_keys}

    # rename keys
    event['contract_address'] = event.pop('address')

    # add additional keys
    for key in ['event_name', 'event_hash']:
        if key not in abi_query:
            raise Exception('should specify ' + str(key))
        event[key] = abi_query[key]

    # add event args
    if arg_prefix is None:
        arg_container = {}
        event['args'] = arg_container
        arg_prefix = ''
    else:
        arg_container = event
    for event_args in [decoded_topics, decoded_data]:
        for arg_name, arg_value in event_args.items():
            key = arg_prefix + arg_name
            if key in arg_container:
                raise Exception('event key collision: ' + str(key))
            arg_container[key] = arg_value

    return event


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
        decoded_data = decode_event_unindexed_data(
            data=value,
            unindexed_types=unindexed_types,
            unindexed_names=unindexed_names,
        )
        for name, subvalue in decoded_data.items():
            decoded[name][index] = subvalue

    # concatenate
    import pandas as pd

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

