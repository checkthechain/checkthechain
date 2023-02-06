from __future__ import annotations

import typing

import toolsql

from ctc import config
from ctc import spec
from .. import abi_utils
from .. import binary_utils


def _parse_event_query_type(
    *,
    contract_address: spec.Address | None,
    event_hash: typing.Any | None,
    topic1: spec.BinaryData | None,
    topic2: spec.BinaryData | None,
    topic3: spec.BinaryData | None,
) -> int:

    # parse input flags
    has_contract = contract_address is not None
    has_event_type = event_hash is not None
    has_other_topics = (
        topic1 is not None or topic2 is not None or topic3 is not None
    )

    # return type based on input flags
    if has_contract and has_event_type and not has_other_topics:
        return 1
    elif not has_contract and has_event_type and not has_other_topics:
        return 2
    elif has_contract and not has_event_type and not has_other_topics:
        return 3
    elif not has_contract and not has_event_type and not has_other_topics:
        return 4
    elif has_contract and has_event_type and has_other_topics:
        return 5
    elif not has_contract and has_event_type and has_other_topics:
        return 6
    elif has_contract and not has_event_type and has_other_topics:
        return 7
    elif not has_contract and not has_event_type and has_other_topics:
        return 8
    else:
        raise Exception('could not parse query type')


async def _async_parse_event_query_args(
    contract_address: spec.Address | None,
    *,
    event_name: str | None,
    event_abi: spec.EventABI | None,
    event_hash: str | None,
    named_topics: typing.Mapping[str, typing.Any] | None,
    decoded_topic1: typing.Any | None = None,
    decoded_topic2: typing.Any | None = None,
    decoded_topic3: typing.Any | None = None,
    encoded_topic1: spec.BinaryData | None = None,
    encoded_topic2: spec.BinaryData | None = None,
    encoded_topic3: spec.BinaryData | None = None,
    context: spec.Context,
) -> tuple[typing.Sequence[spec.BinaryData | None], spec.EventABI | None]:
    """compute encoded topics and event abi of query as needed

    ## Topic Encoding
    - topics are assumed to be encoded if they are of type str and begin wit

    Event hash can be specified by 5 different argument combinations
    - event_hash
    - event_abi
    - encoded_topics
    - contract_address + event_name
    """

    # determine how topics are being specified
    using_encoded_topics = (
        encoded_topic1 is not None
        or encoded_topic2 is not None
        or encoded_topic3 is not None
    )
    using_decoded_topics = (
        decoded_topic1 is not None
        or decoded_topic2 is not None
        or decoded_topic3 is not None
    )
    using_named_topics = named_topics is not None
    if (
        (using_encoded_topics and using_decoded_topics)
        or (using_encoded_topics and using_named_topics)
        or (using_decoded_topics and using_named_topics)
    ):
        raise Exception('should specify topics using only one method')

    # obtain event abi if needed
    if event_hash is not None and event_abi is not None:
        if event_hash != abi_utils.get_event_hash(event_abi):
            raise Exception('conflicting event hashes for given inputs')
    using_name_for_hash = event_hash is None and event_name is not None
    need_event_abi = (
        using_named_topics or using_decoded_topics or using_name_for_hash
    )
    if need_event_abi and event_abi is None:
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=contract_address,
            event_name=event_name,
            event_hash=event_hash,
            context=context,
        )
    if using_name_for_hash and event_abi is None:
        raise Exception('did not obtain proper event abi')

    # parse named event topics
    if named_topics is not None:
        if event_abi is None:
            raise Exception('could not obtain event_abi')
        names = abi_utils.get_event_indexed_names(event_abi)
        if len(names) >= 1 and names[0] in named_topics:
            decoded_topic1 = named_topics[names[0]]
        if len(names) >= 2 and names[1] in named_topics:
            decoded_topic2 = named_topics[names[1]]
        if len(names) >= 3 and names[2] in named_topics:
            decoded_topic3 = named_topics[names[2]]
        for name in named_topics.keys():
            if name not in names:
                raise Exception('unknown topic name: ' + str(name))

    if encoded_topic1 is not None:
        encoded_topic1 = binary_utils.binary_convert(
            encoded_topic1, 'binary', n_bytes=32
        )
    if encoded_topic2 is not None:
        encoded_topic2 = binary_utils.binary_convert(
            encoded_topic2, 'binary', n_bytes=32
        )
    if encoded_topic3 is not None:
        encoded_topic3 = binary_utils.binary_convert(
            encoded_topic3, 'binary', n_bytes=32
        )

    # encode decoded event topics
    if using_decoded_topics or using_named_topics:
        if event_abi is None:
            raise Exception('could not obtain event_abi')
        if decoded_topic1 is not None:
            if len(event_abi['inputs']) < 1:
                raise Exception()
            encoded_topic1 = abi_utils.abi_encode(
                decoded_topic1, event_abi['inputs'][0]['type']
            )
        if decoded_topic2 is not None:
            if len(event_abi['inputs']) < 2:
                raise Exception()
            encoded_topic2 = abi_utils.abi_encode(
                decoded_topic2, event_abi['inputs'][1]['type']
            )
        if decoded_topic3 is not None:
            if len(event_abi['inputs']) < 3:
                raise Exception()
            encoded_topic3 = abi_utils.abi_encode(
                decoded_topic3, event_abi['inputs'][2]['type']
            )

    # return result
    if event_abi is not None:
        event_hash = abi_utils.get_event_hash(event_abi)
    if event_hash is not None:
        encoded_event_hash = binary_utils.binary_convert(event_hash, 'binary')
    else:
        encoded_event_hash = None

    encoded_topics = (
        encoded_event_hash,
        encoded_topic1,
        encoded_topic2,
        encoded_topic3,
    )
    return encoded_topics, event_abi


async def async_scrub_db_queries(
    *,
    contract_address: spec.Address | None,
    event_hash: str | None = None,
    encoded_topic1: spec.BinaryData | None = None,
    encoded_topic2: spec.BinaryData | None = None,
    encoded_topic3: spec.BinaryData | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    context: spec.Context,
) -> None:

    from ctc import db
    from ctc.toolbox import range_utils

    # query queries
    queries = await db.async_query_event_queries(
        contract_address=contract_address,
        event_hash=event_hash,
        topic1=encoded_topic1,
        topic2=encoded_topic2,
        topic3=encoded_topic3,
        start_block=start_block,
        end_block=end_block,
        context=context,
    )
    if queries is None:
        queries = []

    # sort queries into groups
    if typing.TYPE_CHECKING:
        QueryTuple = typing.Tuple[
            int,
            typing.Union[spec.Address, None],
            typing.Union[spec.BinaryData, None],
            typing.Union[spec.BinaryData, None],
            typing.Union[spec.BinaryData, None],
            typing.Union[spec.BinaryData, None],
        ]
    query_sets: typing.MutableMapping[
        QueryTuple, typing.MutableSequence[tuple[int, int]]
    ]
    query_sets = {}
    query_ids: typing.MutableMapping[
        QueryTuple, typing.MutableMapping[tuple[int, int], int]
    ]
    query_ids = {}
    for query in queries:
        if query is None:
            continue
        query_set: QueryTuple = (
            query['query_type'],
            query['contract_address'],
            query['event_hash'],
            query['topic1'],
            query['topic2'],
            query['topic3'],
        )
        query_range = (query['start_block'], query['end_block'])
        query_sets.setdefault(query_set, [])
        query_sets[query_set].append(query_range)
        query_ids.setdefault(query_set, {})
        query_ids[query_set][query_range] = query['query_id']

    # join contiguous and overlapping queries
    to_delete: typing.MutableSequence[int] = []
    to_insert: typing.MutableSequence[spec.EventQuery] = []
    for query_set, query_ranges in query_sets.items():
        scrubbed_lists = range_utils.combine_overlapping_ranges(query_ranges)
        scrubbed = [(qr[0], qr[1]) for qr in scrubbed_lists]
        if len(scrubbed) != len(query_ranges):
            for query_range in query_ranges:
                if query_range not in scrubbed:
                    to_delete.append(query_ids[query_set][query_range])
            for query_range in scrubbed:
                if query_range not in query_ranges:
                    new_query: spec.DBEventQuery = {
                        'query_type': query_set[0],
                        'contract_address': query_set[1],
                        'event_hash': query_set[2],
                        'topic1': query_set[3],
                        'topic2': query_set[4],
                        'topic3': query_set[5],
                        'start_block': query_range[0],
                        'end_block': query_range[1],
                    }
                    to_insert.append(new_query)

    # perform db operations
    db_config = config.get_context_db_config(
        schema_name='events',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        await db.async_delete_event_queries(
            query_ids=to_delete,
            context=context,
            conn=conn,
        )
        await db.async_upsert_event_queries(
            event_queries=to_insert,
            context=context,
            conn=conn,
        )


def print_event_query_summary(
    *,
    contract_address: spec.Address | None,
    event_hash: typing.Any | None,
    topic1: typing.Any | None,
    topic2: typing.Any | None,
    topic3: typing.Any | None,
    start_block: int,
    end_block: int,
) -> None:

    from ctc import cli

    cli.print_bullet(key='contract_address', value=contract_address)
    cli.print_bullet(key='event_hash', value=event_hash)
    cli.print_bullet(key='topic1', value=topic1)
    cli.print_bullet(key='topic2', value=topic2)
    cli.print_bullet(key='topic3', value=topic3)
    cli.print_bullet(key='start_block', value=start_block)
    cli.print_bullet(key='end_block', value=end_block)

