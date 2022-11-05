from __future__ import annotations

import typing

from ctc import spec
from ... import binary_utils
from .. import abi_coding_utils
from . import event_abi_parsing
from . import event_abi_queries


@typing.overload
def decode_event_topics(
    topics: typing.Sequence[spec.BinaryData],
    *,
    use_names: typing.Literal[False],
    event_abi: typing.Optional[spec.EventABI] = None,
    indexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    indexed_names: typing.Optional[list[str]] = None,
) -> list[str]:
    ...


@typing.overload
def decode_event_topics(
    topics: typing.Sequence[spec.BinaryData],
    *,
    use_names: typing.Literal[True],
    event_abi: typing.Optional[spec.EventABI] = None,
    indexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    indexed_names: typing.Optional[list[str]] = None,
) -> dict[str, str]:
    ...


@typing.overload
def decode_event_topics(
    topics: typing.Sequence[spec.BinaryData],
    *,
    event_abi: typing.Optional[spec.EventABI] = None,
    indexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    indexed_names: typing.Optional[list[str]] = None,
    use_names: bool = True,
) -> typing.Union[list[str], dict[str, str]]:
    ...


def decode_event_topics(
    topics: typing.Sequence[spec.BinaryData],
    *,
    event_abi: typing.Optional[spec.EventABI] = None,
    indexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    indexed_names: typing.Optional[list[str]] = None,
    use_names: bool = True,
) -> typing.Union[list[str], dict[str, str]]:
    """decode topic data (i.e. indexed data) of event"""

    # get abi
    if indexed_types is None:
        if event_abi is None:
            raise Exception('must specify event_abi')
        indexed_types = event_abi_parsing.get_event_indexed_types(event_abi)

    # decode
    decoded_topics: list[str] = []
    for topic, indexed_type in zip(topics[1:], indexed_types):
        # only decode value types
        if (
            indexed_type in ['bytes', 'string']
            or indexed_type.endswith(']')
            or indexed_type.endswith(')')
        ):
            decoded_topics.append(topic)  # type: ignore
        else:
            topic = binary_utils.binary_convert(topic, 'binary')
            decoded_topic = abi_coding_utils.abi_decode(topic, indexed_type)
            decoded_topics.append(decoded_topic)

    # package output
    if not use_names:
        return decoded_topics
    else:
        if indexed_names is None:
            if event_abi is None:
                raise Exception('must specify event_abi')
            indexed_names = event_abi_parsing.get_event_indexed_names(event_abi)
        return dict(zip(indexed_names, decoded_topics))


@typing.overload
def decode_event_unindexed_data(
    data: spec.BinaryData,
    *,
    use_names: typing.Literal[False],
    event_abi: typing.Optional[spec.EventABI] = None,
    unindexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    unindexed_names: typing.Optional[list[str]] = None,
) -> list[str]:
    ...


@typing.overload
def decode_event_unindexed_data(
    data: spec.BinaryData,
    *,
    use_names: typing.Literal[True],
    event_abi: typing.Optional[spec.EventABI] = None,
    unindexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    unindexed_names: typing.Optional[list[str]] = None,
) -> dict[str, str]:
    ...


@typing.overload
def decode_event_unindexed_data(
    data: spec.BinaryData,
    *,
    event_abi: typing.Optional[spec.EventABI] = None,
    unindexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    unindexed_names: typing.Optional[list[str]] = None,
    use_names: bool = True,
) -> typing.Union[list[str], dict[str, str]]:
    ...


def decode_event_unindexed_data(
    data: spec.BinaryData,
    *,
    event_abi: typing.Optional[spec.EventABI] = None,
    unindexed_types: typing.Optional[list[spec.ABIDatumType]] = None,
    unindexed_names: typing.Optional[list[str]] = None,
    use_names: bool = True,
) -> typing.Union[list[str], dict[str, str]]:
    """decode the unindexed data of event"""

    # gather metadata
    if unindexed_types is None:
        if event_abi is None:
            raise Exception('must specify event_abi')
        unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)

    # decode data
    data = binary_utils.binary_convert(data, 'binary')
    decoded = abi_coding_utils.abi_decode(
        data, '(' + ','.join(unindexed_types) + ')'
    )

    # package outputs
    if not use_names:
        return list(decoded)
    else:
        if unindexed_names is None:
            if event_abi is None:
                raise Exception('must specify event_abi')
            unindexed_names = event_abi_parsing.get_event_unindexed_names(
                event_abi
            )
        return dict(zip(unindexed_names, decoded))


def normalize_event(
    event: spec.RawLog,
    event_abi: spec.EventABI,
    *,
    arg_prefix: str | None = 'arg__',
) -> spec.NormalizedLog:
    """normalize raw log data into decoded semantic event data"""

    # decode event args
    decoded_topics = decode_event_topics(
        topics=event['topics'],
        event_abi=event_abi,
        use_names=True,
    )
    decoded_data = decode_event_unindexed_data(
        data=event['data'], event_abi=event_abi, use_names=True
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
    # args either stored in 'args' key or directly in normalized event
    if arg_prefix is None:
        arg_container: typing.MutableMapping[typing.Any, typing.Any] = {}
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


async def async_encode_events_dataframe(
    events: spec.DataFrame,
    event_abis: typing.Mapping[str, spec.EventABI],
    *,
    sort_index: bool = True,
) -> spec.DataFrame:

    encoded_groups = {}
    for event_hash, sub_events in events.groupby('event_hash'):

        # get event abi
        if event_abis is not None and event_hash in event_abis:
            event_abi = event_abis[event_hash]
        else:
            if len(sub_events) == 0:
                continue
            else:
                event_abi = await event_abi_queries.async_get_event_abi(
                    event_hash=event_hash,
                    contract_address=sub_events['contract_address'].values[0],
                )

        encoded_groups[event_hash] = encode_events_dataframe_event_type(
            events=sub_events,
            event_abi=event_abi,
        )

    import pandas as pd

    all_events = pd.concat(encoded_groups)

    if sort_index:
        all_events = all_events.sort_index()

    return all_events


def encode_events_dataframe_event_type(
    events: spec.DataFrame,
    event_abi: spec.EventABI,
) -> spec.DataFrame:
    """encode according to a single specific event type"""

    import pandas as pd

    encoded_events: typing.MutableMapping[
        str, typing.Sequence[typing.Any] | spec.Series | None
    ] = {}

    # encode metadata
    for key in [
        'transaction_hash',
        'contract_address',
        'event_hash',
    ]:
        encoded_events[key] = events[key]

    # encode topics
    indexed_names = event_abi_parsing.get_event_indexed_names(event_abi)
    indexed_types = event_abi_parsing.get_event_indexed_types(event_abi)
    for t, (topic_name, topic_type) in enumerate(
        zip(indexed_names, indexed_types)
    ):
        column_name = 'arg__' + topic_name
        decoded_topic = events[column_name]
        encoded_events['topic' + str(t + 1)] = decoded_topic.map(
            lambda x: abi_coding_utils.abi_encode(x, topic_type)
        )

    # encode unindexed data
    unindexed_names = event_abi_parsing.get_event_unindexed_names(event_abi)
    unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)
    if len(unindexed_names) > 0:
        unindexed_columns = ['arg__' + name for name in unindexed_names]
        encoded_events['unindexed'] = [
            abi_coding_utils.abi_encode(tuple(datum), unindexed_types)
            for datum in events[unindexed_columns].values
        ]

    # set unspecified columns to None
    for column_name in ['topic1', 'topic2', 'topic3', 'unindexed']:
        encoded_events.setdefault(column_name, None)

    return pd.DataFrame(encoded_events)


def decode_events_dataframe(
    events: spec.DataFrame,
    event_abi: spec.EventABI,
    *,
    decode_metadata: bool = True,
    decode_topics: bool = True,
    decode_unindexed: bool = True,
) -> spec.DataFrame:
    """decode according to single specific event type"""

    # decode metadata
    if decode_metadata:
        events['contract_address'] = '0x' + events['contract_address'].map(
            bytes.hex
        )
        events['transaction_hash'] = '0x' + events['transaction_hash'].map(
            bytes.hex
        )
        events['event_hash'] = '0x' + events['event_hash'].map(bytes.hex)

    # decode indexed inputs
    if decode_topics:
        indexed_names = event_abi_parsing.get_event_indexed_names(event_abi)
        indexed_types = event_abi_parsing.get_event_indexed_types(event_abi)
        n_indexed_inputs = len(indexed_types)
        if n_indexed_inputs >= 1:
            events['arg__' + indexed_names[0]] = events['topic1'].map(
                lambda x: abi_coding_utils.abi_decode(x, indexed_types[0])
            )
        if n_indexed_inputs >= 2:
            events['arg__' + indexed_names[1]] = events['topic2'].map(
                lambda x: abi_coding_utils.abi_decode(x, indexed_types[1])
            )
        if n_indexed_inputs >= 3:
            events['arg__' + indexed_names[2]] = events['topic3'].map(
                lambda x: abi_coding_utils.abi_decode(x, indexed_types[2])
            )

        if 'topic1' in events.columns:
            del events['topic1']
        if 'topic2' in events.columns:
            del events['topic2']
        if 'topic3' in events.columns:
            del events['topic3']

    # decode unindexed data
    if decode_unindexed:
        unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)
        if len(unindexed_types) > 0:
            import pandas as pd

            unindexed_names = event_abi_parsing.get_event_unindexed_names(
                event_abi
            )
            decode_type_str = '(' + ','.join(unindexed_types) + ')'
            decoded_unindexed_data = map(
                lambda x: abi_coding_utils.abi_decode(x, decode_type_str),  # type: ignore
                events['unindexed'],
            )
            unindexed_column_names = [
                'arg__' + name for name in unindexed_names
            ]
            unindexed_df = pd.DataFrame(
                decoded_unindexed_data, columns=unindexed_column_names
            )

            for column_name, column_value in unindexed_df.items():
                events[column_name] = column_value
            # events = pd.concat([events.reset_index(), unindexed_df], axis=1)
            # events = events.set_index(
            #     ['block_number', 'transaction_index', 'log_index']
            # )

        if 'unindexed' in events:
            del events['unindexed']

    return events


def decode_events_dicts(
    events: typing.Sequence[spec.EncodedEvent],
    event_abi: spec.EventABI,
) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
    return [decode_event_dict(event, event_abi) for event in events]


def decode_event_dict(
    event: spec.EncodedEvent,
    event_abi: spec.EventABI,
) -> typing.Mapping[str, typing.Any]:

    # decode metadata
    event['contract_address'] = binary_utils.binary_convert(
        event['contract_address'],
        'prefix_hex',
    )
    event['transaction_hash'] = binary_utils.binary_convert(
        event['transaction_hash'],
        'prefix_hex',
    )
    event['event_hash'] = binary_utils.binary_convert(
        event['event_hash'],
        'prefix_hex',
    )

    # decode indexed inputs
    indexed_names = event_abi_parsing.get_event_indexed_names(event_abi)
    indexed_types = event_abi_parsing.get_event_indexed_types(event_abi)
    if event.get('topic1') is not None:
        event['arg__' + indexed_names[0]] = abi_coding_utils.abi_decode(  # type: ignore
            event.pop('topic1'),  # type: ignore
            indexed_types[0],
        )
    if event.get('topic2') is not None:
        event['arg__' + indexed_names[1]] = abi_coding_utils.abi_decode(  # type: ignore
            event.pop('topic2'),  # type: ignore
            indexed_types[1],
        )
    if event.get('topic3') is not None:
        event['arg__' + indexed_names[2]] = abi_coding_utils.abi_decode(  # type: ignore
            event.pop('topic3'),  # type: ignore
            indexed_types[2],
        )
    if 'topic1' in event:
        del event['topic1']  # type: ignore
    if 'topic2' in event:
        del event['topic2']  # type: ignore
    if 'topic3' in event:
        del event['topic3']  # type: ignore

    # decode unindexed data
    unindexed_types = event_abi_parsing.get_event_unindexed_types(
        event_abi
    )
    if len(unindexed_types) > 0:
        unindexed_names = event_abi_parsing.get_event_unindexed_names(
            event_abi
        )
        decode_type_str = '(' + ','.join(unindexed_types) + ')'
        decoded_unindexed_data = abi_coding_utils.abi_decode(
            event['unindexed'],
            decode_type_str,
        )
        unindexed_column_names = ['arg__' + name for name in unindexed_names]
        for name, datum in zip(unindexed_column_names, decoded_unindexed_data):
            event['arg__' + name] = datum  # type: ignore
    if 'unindexed' in event:
        del event['unindexed']  # type: ignore

    return event
