from __future__ import annotations

import typing

from ctc import spec
from .. import abi_coding_utils
from . import event_abi_parsing
from . import event_abi_queries

if typing.TYPE_CHECKING:
    from typing import Literal
    import polars as pl


async def async_decode_events_dataframe(
    events: spec.PolarsDataFrame,
    event_abis: typing.Sequence[spec.EventABI]
    | typing.Mapping[str, spec.EventABI]
    | None = None,
    *,
    context: spec.Context,
    column_prefix_type: Literal['arg', 'event_name', 'event_hash']
    | None = None,
    column_prefix: str | None = None,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
) -> spec.PolarsDataFrame:
    """

    columns are prefixed according to input settings
    - column_prefix_type == 'arg' --> use 'arg__' as prefix
    - column_prefix_type == 'event_name' --> use '{event_name}__' as prefix
    - column_prefix_type == 'event_hash' --> use '{event_hash}__' as prefix
    - column_prefix_type == None --> use column_prefix if not None, otherwise ''
    """

    import polars as pl
    from ctc.toolbox import pl_utils

    # package input abi's
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

    # acquire missing event abi's
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

    # remove unused abi's
    abis = {k: v for k, v in abis.items() if k in event_hashes}

    # parse abi information
    all_indexed_types = {}
    all_indexed_names = {}
    all_unindexed_types = {}
    all_unindexed_types = {}
    all_unindexed_names = {}
    all_names = []
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

        all_names.extend(indexed_names)
        all_names.extend(unindexed_names)

    # create dataframe schema
    if column_prefix_type is None and column_prefix is None:
        if len(abis) == 1:
            column_prefix_type = 'arg'
        else:
            event_names = {
                abi.get('name')
                for abi in abis.values()
                if abi.get('name') is not None
            }
            if len(event_names) == len(abis):
                column_prefix_type = 'event_name'
            else:
                column_prefix_type = 'event_hash'
    if column_prefix_type == 'arg':
        column_prefix = 'arg__'
    elif column_prefix_type == 'event_name':
        column_prefix = '{event_name}__'
    elif column_prefix_type == 'event_hash':
        column_prefix = '{event_hash}__'
    else:
        if column_prefix is None:
            column_prefix = ''
    event_hashes = list(all_indexed_types.keys())
    schema = []
    used_names = []
    offsets = [0]
    for event_hash in event_hashes:
        types = all_indexed_types[event_hash] + all_unindexed_types[event_hash]
        names = all_indexed_names[event_hash] + all_unindexed_names[event_hash]
        if '{event_name}' in column_prefix:
            if 'name' in abis[event_hash]:
                event_name = abis[event_hash]['name']
            else:
                raise Exception('event name not specified in event abi')
            used_column_prefix = column_prefix.format(
                event_hash=event_hash,
                event_name=event_name,
            )
        else:
            used_column_prefix = column_prefix.format(event_hash=event_hash)
        for abi_type, name in zip(types, names):
            name = used_column_prefix + name
            if name in used_names:
                raise Exception('naming conflict ' + str(name))
            pl_type = _abi_type_to_polars_dtype(abi_type)
            schema.append((name, pl_type))
            used_names.append(name)
        offsets.append(len(schema))
    event_hash_offsets = dict(zip(event_hashes, offsets))

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
    decoded_events: typing.Sequence[typing.Sequence[typing.Any]] = [
        [] for i in range(len(schema))
    ]
    for e, event_hash in enumerate(events['event_hash'].to_list()):

        i = event_hash_offsets[event_hash]

        for c in range(i):
            decoded_events[c].append(None)

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
                value = topic[e]
            else:
                value = abi_coding_utils.abi_decode(topic[e], indexed_type)
            decoded_events[i].append(value)
            i = i + 1

        # decode unindexed data
        if len(all_unindexed_types[event_hash]) > 0:
            unindexed_types = all_unindexed_types[event_hash]
            unindexed_names = all_unindexed_names[event_hash]
            unindexed_decoded = abi_coding_utils.abi_decode(
                unindexed[e],
                unindexed_types,
            )
            for value in unindexed_decoded:
                decoded_events[i].append(value)
                i = i + 1

        for c in range(i, len(schema)):
            decoded_events[c].append(None)

    # convert to dataframe
    decoded = pl.DataFrame(decoded_events, schema=schema, orient='col')

    # convert binary columns to hex
    if binary_output_format == 'prefix_hex':
        decoded = pl_utils.binary_columns_to_prefix_hex(decoded)

    return decoded


def _abi_type_to_polars_dtype(abi_type: str) -> pl.datatypes.DataTypeClass:
    import polars as pl

    if abi_type == 'bool':
        return pl.datatypes.Boolean
    elif abi_type == 'address':
        return pl.datatypes.Utf8
    elif abi_type == 'string':
        return pl.datatypes.Utf8
    elif abi_type in ['bytes', 'bytes8', 'bytes16', 'bytes24', 'bytes32']:
        return pl.datatypes.Binary
    elif abi_type == 'function':
        return pl.datatypes.Object
    elif abi_type in [
        'int8',
        'int16',
        'int24',
        'int32',
        'int40',
        'int48',
        'int56',
        'int64',
        'uint8',
        'uint16',
        'uint24',
        'uint32',
    ]:
        return pl.datatypes.Int64
    elif abi_type in [
        'int72',
        'int80',
        'int88',
        'int96',
        'int104',
        'int112',
        'int120',
        'int128',
        'int136',
        'int144',
        'int152',
        'int160',
        'int168',
        'int176',
        'int184',
        'int192',
        'int200',
        'int208',
        'int216',
        'int224',
        'int232',
        'int240',
        'int248',
        'int256',
        'uint72',
        'uint80',
        'uint88',
        'uint96',
        'uint104',
        'uint112',
        'uint120',
        'uint128',
        'uint136',
        'uint144',
        'uint152',
        'uint160',
        'uint168',
        'uint176',
        'uint184',
        'uint192',
        'uint200',
        'uint208',
        'uint216',
        'uint224',
        'uint232',
        'uint240',
        'uint248',
        'uint256',
    ]:
        return pl.datatypes.Object
    elif (
        abi_type.startswith('fixed') or abi_type.startswith('ufixed')
    ) and not abi_type.endswith(']'):
        return pl.datatypes.Decimal
    elif abi_type.endswith(']') or abi_type.endswith(')'):
        return pl.datatypes.Object
    else:
        raise Exception('unknown abi type')

