from __future__ import annotations

import typing

from ctc import spec
from .. import abi_coding_utils
from . import event_abi_parsing
from . import event_abi_queries


async def async_decode_events_dataframe(
    events: spec.PolarsDataFrame,
    event_abis: typing.Sequence[spec.EventABI]
    | typing.Mapping[str, spec.EventABI]
    | None = None,
    *,
    context: spec.Context,
) -> typing.Sequence[typing.Mapping[str, typing.Any]]:

    import polars as pl

    # package input abis
    if isinstance(event_abis, dict):
        abis = event_abis
    elif event_abis is None:
        abis = {}
    elif isinstance(event_abis, list):
        abis: typing.Mapping[str, spec.Event] = {}
        for event_abi in event_abis:
            event_hash = event_abi_parsing.get_event_hash(event_abi)
            abis[event_hash] = event_abi
    else:
        raise Exception()

    # acquire missing event abis
    event_hashes = list(events['event_hash'].unique())
    missing_event_types = set(event_hashes) - set(abis.keys())
    if len(missing_event_types) > 0:
        import asyncio

        event_types = events.groupby('event_hash').agg(
            pl.col('contract_address').unique()
        )
        coroutines = []
        for event_hash, contract_addresses in event_types.rows():
            coroutine = event_abi_queries.async_get_event_abi(
                event_hash=event_hash,
                contract_addresses=contract_addresses,
                context=context,
            )
            coroutines.append(coroutine)
        new_event_abis = await asyncio.gather(*coroutines)
        abis.update(
            dict(zip(event_types['event_hash'].to_list(), new_event_abis))
        )

    # parse abi information
    all_indexed_types = {}
    all_indexed_names = {}
    all_unindexed_types = {}
    all_unindexed_types = {}
    all_unindexed_names = {}
    n_decode_topics = 0
    decode_unindexed = False
    for event_hash, event_abi in abis.items():

        indexed_types = event_abi_parsing.get_event_indexed_types(event_abi)
        indexed_names = event_abi_parsing.get_event_indexed_names(event_abi)
        all_indexed_types[event_hash] = indexed_types
        all_indexed_names[event_hash] = indexed_names
        n_decode_topics = max(n_decode_topics, len(indexed_types))

        unindexed_types = event_abi_parsing.get_event_unindexed_types(event_abi)
        unindexed_names = event_abi_parsing.get_event_unindexed_names(event_abi)
        all_unindexed_types[event_hash] = unindexed_types
        all_unindexed_names[event_hash] = unindexed_names
        if len(unindexed_types) > 0:
            decode_unindexed = True

    # create iterators for relevant columns
    if n_decode_topics >= 1:
        topic1 = events['topic1'].to_list()
    else:
        topic1 = None
    if n_decode_topics >= 2:
        topic2 = events['topic2'].to_list()
    else:
        topic2 = None
    if n_decode_topics >= 3:
        topic3 = events['topic3'].to_list()
    else:
        topic3 = None
    if decode_unindexed:
        unindexed = events['unindexed'].to_list()
    topics = [topic1, topic2, topic3]

    # decode
    decoded_events = []
    for e, event_hash in enumerate(events['event_hash'].to_list()):

        decoded_event = {}

        # decode indexed data
        indexed_types = all_indexed_types[event_hash]
        indexed_names = all_indexed_names[event_hash]
        for indexed_type, indexed_name, topic in zip(
            indexed_types, indexed_names, topics
        ):
            if (
                indexed_type in ['bytes', 'string']
                or indexed_type.endswith(']')
                or indexed_type.endswith(')')
            ):
                decoded_event[indexed_name] = topic[e]
            else:
                decoded_event[indexed_name] = abi_coding_utils.abi_decode(
                    topic[e], indexed_type
                )

        # decode unindexed data
        if len(unindexed_types) > 0:
            unindexed_types = all_unindexed_types[event_hash]
            unindexed_names = all_unindexed_names[event_hash]
            unindexed_decoded = abi_coding_utils.abi_decode(
                unindexed[e],
                unindexed_types,
            )
            decoded_event.update(dict(zip(unindexed_names, unindexed_decoded)))

        decoded_events.append(decoded_event)

    return decoded_events

