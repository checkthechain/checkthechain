from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import block_utils
from . import event_db_read
from . import event_node_read

if typing.TYPE_CHECKING:
    import tooltime


async def async_get_events(
    contract_address: spec.Address | None,
    *,
    event_name: str | None = None,
    event_hash: str | None = None,
    event_abi: spec.EventABI | None = None,
    topics: typing.Sequence[typing.Any]
    | typing.Mapping[str, typing.Any]
    | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    keep_multiindex: bool = True,
    use_db: bool = True,
    read_from_db: bool | None = None,
    write_to_db: bool | None = None,
    provider: spec.ProviderReference = None,
    allow_suboptimal_queries: bool = False,
    decode: bool = True,
) -> spec.DataFrame:
    """ """

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
    topics, event_abi = await _async_get_event_query_metadata(
        contract_address=contract_address,
        event_name=event_name,
        event_hash=event_hash,
        event_abi=event_abi,
        topics=topics,
        decode=decode,
    )

    # query data from db and/or node
    if read_from_db:
        events = await event_db_read._async_query_events_from_node_and_db(
            contract_address=contract_address,
            topics=topics,
            start_block=start_block,
            end_block=end_block,
            write_to_db=write_to_db,
            provider=provider,
        )
    else:
        events = await event_node_read._async_query_events_from_node(
            contract_address=contract_address,
            topics=topics,
            start_block=start_block,
            end_block=end_block,
            write_to_db=write_to_db,
            provider=provider,
        )

    if decode:
        pass

    if not keep_multiindex:
        events.index = events.index.get_level_values('block_number')

    if include_timestamps:
        timestamps = await async_get_event_timestamps(events, provider=provider)
        events.insert(0, 'timestamp', timestamps)  # type: ignore

    return events


async def _async_parse_event_query_type(
    *,
    contract_address: spec.Address | None,
    topics: typing.Sequence[typing.Any] | None,
    start_block: int,
    end_block: int,
) -> int:

    if start_block is None or end_block is None:
        raise Exception('query must specify block range')

    if topics is None or len(topics) == 0 or topics[0] is None:
        if (
            topics is not None
            and len(topics) >= 2
            and any(topic is not None for topic in topics[1:])
        ):
            return 7

        if contract_address is None:
            return 6
        else:
            return 4
    else:
        if len(topics) == 1 or all(topic is None for topic in topics[1:]):
            if contract_address is None:
                return 5
            else:
                return 3
        else:
            if contract_address is None:
                return 2
            else:
                return 1


async def _async_get_event_query_metadata(
    contract_address: spec.Address | None,
    *,
    event_name: str | None,
    event_hash: str | None,
    event_abi: spec.EventABI | None,
    topics: typing.Sequence[typing.Any]
    | typing.Mapping[str, typing.Any]
    | None,
    decode: bool,
) -> tuple[typing.Sequence[typing.Any] | None, spec.EventABI | None]:
    """compute topics and event abi of query as needed"""

    # get event abi if needed
    need_event_abi = decode or isinstance(topics, dict)
    if (
        contract_address is not None
        and (event_name is not None or event_hash is not None)
        and event_abi is None
        and need_event_abi
    ):
        event_abi = await abi_utils.async_get_event_abi(
            contract_address=contract_address,
            event_name=event_name,
            event_hash=event_hash,
        )
    if need_event_abi and event_abi is None:
        if decode:
            raise Exception('could not locate event_abi for decoding events')
        elif isinstance(topics, dict):
            raise Exception('could not locate event_abi for sequencing topics')
        else:
            raise Exception('could not obtain event_abi')

    # get event hash
    if event_abi is not None:
        if event_hash is None:
            event_hash = abi_utils.get_event_hash(event_abi)
        else:
            actual_event_hash = abi_utils.get_event_hash(event_abi)
            if event_hash != actual_event_hash:
                raise Exception('event_hash does not match event_abi')

    # convert named topics to list of topics
    if isinstance(topics, dict):
        if event_abi is None:
            raise Exception(
                'if providing named topics, must also provide parameters'
            )

        # add event_hash to topics
        indexed_names = abi_utils.get_event_indexed_names(event_abi)
        for name in topics:
            if name not in indexed_names:
                raise Exception('unknown event topic: ' + str(name))

        # convert topics to map
        topics = [event_hash] + [topics.get(name) for name in indexed_names]
    topics = typing.cast(typing.Union[typing.Sequence[typing.Any], None], None)

    # ensure consistency of event_hash hashes
    if event_hash is not None:
        if topics is None or len(topics) == 0:
            topics = [event_hash]
        elif topics[0] is None:
            topics = [event_hash] + [topic for topic in topics[1:]]
        elif topics[0] != event_hash:
            raise Exception('event hash does not match given topic')

    return topics, event_abi


async def async_get_event_timestamps(
    events: spec.DataFrame,
    provider: spec.ProviderReference = None,
) -> typing.Sequence[int]:

    # get block_numbers
    multi_index = 'block_number' in events.index.names
    if multi_index:
        block_numbers = events.index.get_level_values('block_number')
    else:
        block_numbers = events.index.values

    # get timestamps
    return await block_utils.async_get_block_timestamps(
        block_numbers,
        provider=provider,
    )
