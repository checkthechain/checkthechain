from __future__ import annotations

import typing

from ctc import spec
from .. import formats
from . import abi_coding
from . import event_parsing


def decode_event_topics(
    topics: typing.Sequence[spec.BinaryData],
    event_abi: typing.Optional[spec.EventABI] = None,
    indexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    indexed_names: typing.Optional[list[str]] = None,
    use_names: bool = True,
):
    """
    remaining edgecase:
    - variable data in indexed topic?
    """

    # get abi
    if indexed_types is None:
        if event_abi is None:
            raise Exception('must specify event_abi')
        indexed_types = event_parsing.get_event_indexed_types(event_abi)

    # decode
    decoded_topics = []
    for topic, indexed_type in zip(topics[1:], indexed_types):
        topic = formats.convert(topic, 'binary')
        decoded_topic = abi_coding.abi_decode(topic, indexed_type)
        decoded_topics.append(decoded_topic)

    # package output
    if not use_names:
        return decoded_topics
    else:
        if indexed_names is None:
            if event_abi is None:
                raise Exception('must specify event_abi')
            indexed_names = event_parsing.get_event_indexed_names(event_abi)
        return dict(zip(indexed_names, decoded_topics))


def decode_event_unindexed_data(
    data: spec.BinaryData,
    event_abi: typing.Optional[spec.EventABI] = None,
    unindexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    unindexed_names: typing.Optional[list[str]] = None,
    use_names: bool = True,
):
    """decode the unindexed data of event"""

    # gather metadata
    if unindexed_types is None:
        if event_abi is None:
            raise Exception('must specify event_abi')
        unindexed_types = event_parsing.get_event_unindexed_types(event_abi)

    # decode data
    data = formats.convert(data, 'binary')
    decoded = abi_coding.abi_decode(data, '(' + ','.join(unindexed_types) + ')')

    # package outputs
    if not use_names:
        return decoded
    else:
        if unindexed_names is None:
            if event_abi is None:
                raise Exception('must specify event_abi')
            unindexed_names = event_parsing.get_event_unindexed_names(event_abi)
        return dict(zip(unindexed_names, decoded))


def normalize_event(
    event: spec.RawLog,
    event_abi: spec.EventABI,
    arg_prefix: str = 'arg__',
) -> spec.NormalizedLog:

    # decode event args
    decoded_topics = decode_event_topics(
        topics=event['topics'], event_abi=event_abi
    )
    decoded_data = decode_event_unindexed_data(
        data=event['data'], event_abi=event_abi
    )

    # remove keys
    remove_keys = ['data', 'topics', 'removed']
    normalized = {k: v for k, v in event.items() if k not in remove_keys}

    # rename keys
    normalized['contract_address'] = normalized['address']

    # add additional keys
    normalized['event_name'] = event_abi['name']
    normalized['event_hash'] = event['topics'][0]

    # add event args
    if arg_prefix is None:
        arg_container = {}
        normalized['args'] = arg_container
        arg_prefix = ''
    else:
        arg_container = normalized
    for event_args in [decoded_topics, decoded_data]:
        for arg_name, arg_value in event_args.items():
            key = arg_prefix + arg_name
            if key in arg_container:
                raise Exception('event key collision: ' + str(key))
            arg_container[key] = arg_value

    return normalized


#
# # dataframes
#


def decode_events_dataframe(
    df: spec.DataFrame,
    event_abi: spec.EventABI,
    delete_data_column: bool = True,
) -> spec.DataFrame:
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

