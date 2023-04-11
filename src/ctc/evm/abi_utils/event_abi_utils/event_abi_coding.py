from __future__ import annotations

import typing

from ctc import spec
from ... import binary_utils
from .. import abi_coding_utils
from . import event_abi_parsing


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
            topic = binary_utils.to_binary(topic)
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
    data = binary_utils.to_binary(data)
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

