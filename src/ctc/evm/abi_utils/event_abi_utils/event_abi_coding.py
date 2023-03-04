from __future__ import annotations

import math
import typing
from typing_extensions import Literal

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
    event_abis: typing.Mapping[str, spec.EventABI] | None = None,
    *,
    sort_index: bool = True,
    context: spec.Context = None,
) -> spec.DataFrame:
    """encode the fields of an events dataframe"""

    encoded_groups = {}
    for eh, sub_events in events.groupby('event_hash'):

        event_hash = typing.cast(str, eh)

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
                    context=context,
                )

        if len(set(sub_events['contract_address'])) > 1:
            raise NotImplementedError(
                're-encoding implemented only for single contracts'
            )

        encoded_groups[event_hash] = encode_events_dataframe_event_type(
            events=sub_events,
            event_abi=event_abi,
        )

    import pandas as pd

    all_events = pd.concat(list(encoded_groups.values()))

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
        str, float | typing.Sequence[typing.Any] | spec.Series | None
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

        new_column = []
        for value in events['arg__' + topic_name].values.astype(object):
            encoded = binary_utils.binary_convert(
                abi_coding_utils.abi_encode(value, topic_type),
                'prefix_hex',
            )
            new_column.append(encoded)
        encoded_events['topic' + str(t + 1)] = new_column

    # encode unindexed data
    unindexed_names = event_abi_parsing.get_event_unindexed_names(event_abi)
    unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)
    if len(unindexed_names) > 0:
        unindexed_columns = ['arg__' + name for name in unindexed_names]
        new_column = []
        for datum in events[unindexed_columns].values.astype(object):
            encoded = binary_utils.binary_convert(
                abi_coding_utils.abi_encode(tuple(datum), unindexed_types),
                'prefix_hex',
            )
            new_column.append(encoded)
        encoded_events['unindexed'] = new_column

    # set unspecified columns to None
    for column_name in ['topic1', 'topic2', 'topic3', 'unindexed']:
        encoded_events.setdefault(column_name, float('nan'))

    # create dataframe
    column_order = [
        'transaction_hash',
        'contract_address',
        'event_hash',
        'topic1',
        'topic2',
        'topic3',
        'unindexed',
    ]
    return pd.DataFrame(encoded_events)[column_order]


# def _encode_column(series: spec.Series, abi_type: str) -> spec.Series:
#     import pandas as pd

#     encoded = []
#     for value in series.values:
#         if value is not None and not (
#             isinstance(value, float) and math.isnan(value)
#         ):
#             datum = abi_coding_utils.abi_encode(value, abi_type)
#         else:
#             datum = None
#         encoded.append(datum)

#     return pd.Series(encoded, index=series.index)


def _get_decoded_event_column_names(
    event_abi: spec.EventABI | typing.Sequence[spec.EventABI],
) -> typing.Sequence[str]:
    """get columns of dataframe of decoded event type(s)"""

    if isinstance(event_abi, dict):
        arg_names = event_abi_parsing.get_event_indexed_names(
            event_abi
        ) + event_abi_parsing.get_event_unindexed_names(event_abi)
    elif isinstance(event_abi, list):
        arg_names = []
        for sub_event_abi in event_abi:
            sub_arg_names = event_abi_parsing.get_event_indexed_names(
                sub_event_abi
            ) + event_abi_parsing.get_event_unindexed_names(sub_event_abi)
            for name in sub_arg_names:
                if name not in arg_names:
                    arg_names.append(name)
    else:
        raise Exception('unknown format: ' + str(type(event_abi)))

    return spec.decoded_event_fields + ['arg__' + name for name in arg_names]


async def _async_decode_events_dataframe_old(
    events: spec.DataFrame,
    *,
    event_abis: typing.Mapping[str | tuple[str, str], spec.EventABI]
    | None = None,
    single_event_abi: spec.EventABI | None = None,
    sort_index: bool = True,
    decode_metadata: bool = True,
    decode_topics: bool = True,
    decode_unindexed: bool = True,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    output_format: Literal['dict', 'dataframe'],
    share_abis_across_contracts: bool = True,
    context: spec.Context = None,
) -> spec.DataFrame:
    """encode the fields of an events dataframe

    if single_event_abi=True, all events decoded according to same event abi
    """

    import pandas as pd
    from ctc.toolbox import pd_utils

    if event_abis is None:
        event_abis = {}

    decoded_groups: typing.MutableMapping[str | None, spec.DataFrame] = {}

    if single_event_abi is not None:
        decoded_groups[None] = decode_events_dataframe_event_type(
            events=events,
            event_abi=single_event_abi,
            decode_metadata=decode_metadata,
            decode_topics=decode_topics,
            decode_unindexed=decode_unindexed,
            binary_output_format=binary_output_format,
        )

    else:

        for eh, event_type_events in events.groupby('event_hash'):

            event_hash = typing.cast(str, eh)

            # get event abi
            if share_abis_across_contracts:

                # use single event abi across all addresses
                if event_abis is not None and event_hash in event_abis:
                    event_abi = event_abis[event_hash]
                else:
                    if len(event_type_events) == 0:
                        continue
                    else:
                        contract_address = event_type_events[
                            'contract_address'
                        ].values[0]
                        event_abi = await event_abi_queries.async_get_event_abi(
                            event_hash=event_hash,
                            contract_address=contract_address,
                            context=context,
                        )

                # decode using event_abi
                decoded_groups[event_hash] = decode_events_dataframe_event_type(
                    events=event_type_events,
                    event_abi=event_abi,
                    decode_metadata=decode_metadata,
                    decode_topics=decode_topics,
                    decode_unindexed=decode_unindexed,
                    binary_output_format=binary_output_format,
                )

            else:

                # handle each contract separately
                groups = event_type_events.groupby('contract_address')
                events_by_contract = {}
                event_abis = dict(event_abis)
                for contract_address, contract_events in groups:

                    # use event abi specific to contract
                    key = (contract_address, event_hash)
                    if key not in event_abis:
                        event_abis[
                            key  # type: ignore
                        ] = await event_abi_queries.async_get_event_abi(
                            event_hash=event_hash,
                            contract_address=contract_address,  # type: ignore
                            context=context,
                        )
                    event_abi = event_abis[key]  # type: ignore

                    # contract
                    events_by_contract[
                        contract_address
                    ] = decode_events_dataframe_event_type(
                        events=contract_events,
                        event_abi=event_abi,
                        decode_metadata=decode_metadata,
                        decode_topics=decode_topics,
                        decode_unindexed=decode_unindexed,
                        binary_output_format=binary_output_format,
                    )

                contents = list(events_by_contract.values())
                decoded_groups[event_hash] = pd.concat(contents)

    if output_format == 'dataframe':

        contents = list(decoded_groups.values())
        if all(len(subcontents) == 0 for subcontents in contents):
            event_abi_list = list(event_abis.values())
            if single_event_abi is not None:
                event_abi_list.append(single_event_abi)
            # TODO: need to trim here for partial loading
            columns = _get_decoded_event_column_names(event_abi_list)
            all_events = pd_utils.create_empty_dataframe(
                column_names=columns,
                index_names=spec.event_index_fields,
            )
        else:
            all_events = pd.concat(contents)

        if sort_index:
            all_events = all_events.sort_index()

        return all_events

    elif output_format == 'dict':

        decoded_events: typing.Sequence[typing.Mapping[str, typing.Any]] = [
            event  # type: ignore
            for decoded_group in decoded_groups.values()
            for event in decoded_group.reset_index().to_dict(orient='records')
        ]

        if sort_index:
            decoded_events = sorted(
                decoded_events,
                key=lambda event: (event['block_number'], event['log_index']),
            )

        return decoded_events  # type: ignore

    else:
        raise Exception('unknown output format: ' + str(output_format))


def decode_events_dataframe_event_type(
    events: spec.DataFrame,
    event_abi: spec.EventABI,
    *,
    binary_output_format: Literal['prefix_hex', 'binary'] = 'prefix_hex',
    decode_metadata: bool = True,
    decode_topics: bool = True,
    decode_unindexed: bool = True,
) -> spec.DataFrame:
    """decode according to single specific event type"""

    import pandas as pd

    # decode metadata
    if decode_metadata:

        if 'contract_address' in events.columns:
            events['contract_address'] = '0x' + events['contract_address'].map(
                bytes.hex
            )
        if 'transaction_hash' in events.columns:
            events['transaction_hash'] = '0x' + events['transaction_hash'].map(
                bytes.hex
            )
        if 'event_hash' in events.columns:
            events['event_hash'] = '0x' + events['event_hash'].map(bytes.hex)

    # decode indexed inputs
    if decode_topics:
        indexed_names = event_abi_parsing.get_event_indexed_names(event_abi)
        indexed_types = event_abi_parsing.get_event_indexed_types(event_abi)
        n_indexed_inputs = len(indexed_types)

        for i, topic, indexed_name, indexed_type in zip(
            [1, 2, 3],
            ['topic1', 'topic2', 'topic3'],
            indexed_names,
            indexed_types,
        ):
            if topic in events.columns:
                if n_indexed_inputs >= i:
                    name = 'arg__' + indexed_name
                    events[name] = _decode_column(
                        events[topic],
                        indexed_type,
                        binary_output_format=binary_output_format,
                    )

        for topic in ['topic1', 'topic2', 'topic3']:
            if topic in events.columns:
                del events[topic]

    # decode unindexed data
    if decode_unindexed and 'unindexed' in events:
        unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)
        if len(unindexed_types) > 0:

            names = event_abi_parsing.get_event_unindexed_names(event_abi)
            unindexed_columns = ['arg__' + name for name in names]

            decode_type_str = '(' + ','.join(unindexed_types) + ')'
            decoded = [
                abi_coding_utils.abi_decode(datum, decode_type_str)
                for datum in events['unindexed']
            ]
            unindexed_df = pd.DataFrame(decoded, columns=unindexed_columns)
            unindexed_df.index = events.index

            for column_name, column_value in unindexed_df.items():
                events[column_name] = column_value

        del events['unindexed']

    return events


def _decode_column(
    series: spec.Series,
    abi_type: str,
    *,
    binary_output_format: Literal['prefix_hex', 'binary'] = 'prefix_hex',
) -> spec.Series:
    import pandas as pd

    decoded = []
    for value in series.values:
        if value is not None and not (
            isinstance(value, float) and math.isnan(value)
        ):
            if abi_type in ['string', 'bytes', 'bytes32'] or abi_type[-1] in (
                ')',
                ']',
            ):
                datum = binary_utils.binary_convert(value, binary_output_format)
            else:
                datum = abi_coding_utils.abi_decode(value, abi_type)
        else:
            datum = None
        decoded.append(datum)

    return pd.Series(decoded, index=series.index, dtype=object)


def decode_events_dicts(
    events: typing.Sequence[spec.EncodedEvent],
    event_abi: spec.EventABI,
) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
    """decode a list of event dicts"""
    return [decode_event_dict(event, event_abi) for event in events]


def decode_event_dict(
    event: spec.EncodedEvent,
    event_abi: spec.EventABI,
) -> typing.Mapping[str, typing.Any]:
    """decode fields of an event dict"""

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
    unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)
    if len(unindexed_types) > 0:
        unindexed_names = event_abi_parsing.get_event_unindexed_names(event_abi)
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
