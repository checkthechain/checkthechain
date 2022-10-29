from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import binary_utils
from .. import block_utils
from .. import network_utils

if typing.TYPE_CHECKING:
    import tooltime

    from typing_extensions import Literal


async def async_get_events(
    contract_address: spec.Address | None,
    *,
    event_name: str | None = None,
    event_abi: spec.EventABI | None = None,
    event_hash: str | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    keep_multiindex: bool = True,
    use_db: bool = True,
    read_from_db: bool | None = None,
    write_to_db: bool | None = None,
    decode: bool = True,
    provider: spec.ProviderReference = None,
    network: spec.NetworkReference | None = None,
    named_topics: typing.Mapping[str, typing.Any] | None = None,
    decoded_topic1: typing.Any | None = None,
    decoded_topic2: typing.Any | None = None,
    decoded_topic3: typing.Any | None = None,
    encoded_topic1: spec.BinaryData | None = None,
    encoded_topic2: spec.BinaryData | None = None,
    encoded_topic3: spec.BinaryData | None = None,
    verbose: int | bool = 1,
    output_format: Literal['dataframe', 'dict'] = 'dataframe',
) -> spec.DataFrame | typing.Sequence[typing.Mapping[str, typing.Any]]:
    """get events"""

    from . import event_hybrid_queries
    from . import event_node_utils
    from . import event_query_utils
    from . import event_timestamps

    network, provider = network_utils.get_network_and_provider(
        network, provider
    )

    # determine how much to use db
    if read_from_db is None:
        read_from_db = use_db
    if write_to_db is None:
        write_to_db = use_db

    # determine start and end block
    start_block, end_block = await block_utils.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=False,
        to_int=True,
    )

    # get event query metadata
    (
        encoded_topics,
        event_abi,
    ) = await event_query_utils._async_parse_event_query_args(
        contract_address=contract_address,
        event_name=event_name,
        event_hash=event_hash,
        event_abi=event_abi,
        named_topics=named_topics,
        decoded_topic1=decoded_topic1,
        decoded_topic2=decoded_topic2,
        decoded_topic3=decoded_topic3,
        encoded_topic1=encoded_topic1,
        encoded_topic2=encoded_topic2,
        encoded_topic3=encoded_topic3,
        decode_output=decode,
        network=network,
    )

    # query data from db and/or node
    if read_from_db:
        events = (
            await event_hybrid_queries._async_query_events_from_node_and_db(
                contract_address=contract_address,
                event_hash=encoded_topics[0],
                topic1=encoded_topics[1],
                topic2=encoded_topics[2],
                topic3=encoded_topics[3],
                start_block=start_block,
                end_block=end_block,
                write_to_db=write_to_db,
                provider=provider,
                verbose=verbose,
                network=network,
            )
        )
    else:
        events = await event_node_utils._async_query_events_from_node(
            contract_address=contract_address,
            event_hash=encoded_topics[0],
            topic1=encoded_topics[1],
            topic2=encoded_topics[2],
            topic3=encoded_topics[3],
            start_block=start_block,
            end_block=end_block,
            write_to_db=write_to_db,
            provider=provider,
            verbose=verbose,
        )

    if output_format == 'dataframe':
        import pandas as pd

        df = pd.DataFrame(events)

        if decode:
            if event_abi is None:
                raise Exception('could not determine event_abi for decoding')
            df = _decode_events_dataframe(df, event_abi=event_abi)

        if keep_multiindex:
            index_fields = [
                'block_number',
                'transaction_index',
                'log_index',
            ]
            df = df.set_index(index_fields)
        else:
            df.index = df.index.get_level_values('block_number')

        if include_timestamps:
            timestamps = await event_timestamps.async_get_event_timestamps(
                df,
                provider=provider,
            )
            df.insert(0, 'timestamp', timestamps)  # type: ignore

        return df

    elif output_format == 'dict':

        if decode:
            if event_abi is None:
                raise Exception('could not determine event_abi for decoding')
            decoded_events = _decode_events_dicts(events, event_abi)

            return decoded_events

        return events

    else:
        raise Exception('unknown output format: ' + str(output_format))


def _decode_events_dataframe(
    events: spec.DataFrame,
    event_abi: spec.EventABI,
) -> spec.DataFrame:

    # decode metadata
    events['contract_address'] = events['contract_address'].map(
        lambda x: binary_utils.binary_convert(x, 'prefix_hex')
    )
    events['transaction_hash'] = events['transaction_hash'].map(
        lambda x: binary_utils.binary_convert(x, 'prefix_hex')
    )
    events['event_hash'] = events['event_hash'].map(
        lambda x: binary_utils.binary_convert(x, 'prefix_hex')
    )

    # decode indexed inputs
    indexed_names = abi_utils.get_event_indexed_names(event_abi)
    indexed_types = abi_utils.get_event_indexed_types(event_abi)
    n_indexed_inputs = len(indexed_types)
    if n_indexed_inputs >= 1:
        events['arg__' + indexed_names[0]] = events['topic1'].map(
            lambda x: abi_utils.abi_decode(x, indexed_types[0])
        )
    if n_indexed_inputs >= 2:
        events['arg__' + indexed_names[1]] = events['topic2'].map(
            lambda x: abi_utils.abi_decode(x, indexed_types[1])
        )
    if n_indexed_inputs >= 3:
        events['arg__' + indexed_names[2]] = events['topic3'].map(
            lambda x: abi_utils.abi_decode(x, indexed_types[2])
        )

    if 'topic1' in events.columns:
        del events['topic1']
    if 'topic2' in events.columns:
        del events['topic2']
    if 'topic3' in events.columns:
        del events['topic3']

    # decode unindexed data
    unindexed_types = abi_utils.get_event_unindexed_types(event_abi)
    if len(unindexed_types) > 0:
        import pandas as pd

        unindexed_names = abi_utils.get_event_unindexed_names(event_abi)
        decode_type_str = '(' + ','.join(unindexed_types) + ')'
        decoded_unindexed_data = map(
            lambda x: abi_utils.abi_decode(x, decode_type_str),  # type: ignore
            events['unindexed'],
        )
        unindexed_column_names = ['arg__' + name for name in unindexed_names]
        unindexed_df = pd.DataFrame(
            decoded_unindexed_data, columns=unindexed_column_names
        )
        events = pd.concat([events, unindexed_df], axis=1)
    del events['unindexed']

    return events


def _decode_events_dicts(
    events: typing.Sequence[spec.EncodedEvent],
    event_abi: spec.EventABI,
) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
    return [_decode_event_dict(event, event_abi) for event in events]


def _decode_event_dict(
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
    indexed_names = abi_utils.get_event_indexed_names(event_abi)
    indexed_types = abi_utils.get_event_indexed_types(event_abi)
    if event.get('topic1') is not None:
        event['arg__' + indexed_names[0]] = abi_utils.abi_decode(  # type: ignore
            event.pop('topic1'),  # type: ignore
            indexed_types[0],
        )
    if event.get('topic2') is not None:
        event['arg__' + indexed_names[1]] = abi_utils.abi_decode(  # type: ignore
            event.pop('topic2'),  # type: ignore
            indexed_types[1],
        )
    if event.get('topic3') is not None:
        event['arg__' + indexed_names[2]] = abi_utils.abi_decode(  # type: ignore
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
    unindexed_types = abi_utils.get_event_unindexed_types(event_abi)
    if len(unindexed_types) > 0:
        unindexed_names = abi_utils.get_event_unindexed_names(event_abi)
        decode_type_str = '(' + ','.join(unindexed_types) + ')'
        decoded_unindexed_data = abi_utils.abi_decode(
            event['unindexed'],
            decode_type_str,
        )
        unindexed_column_names = ['arg__' + name for name in unindexed_names]
        for name, datum in zip(unindexed_column_names, decoded_unindexed_data):
            event['arg__' + name] = datum  # type: ignore
    if 'unindexed' in event:
        del event['unindexed']  # type: ignore

    return event
