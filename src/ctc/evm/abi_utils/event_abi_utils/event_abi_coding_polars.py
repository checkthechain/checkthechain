from __future__ import annotations

import typing

from ctc import spec
from .. import abi_coding_utils
from . import event_abi_parsing
from . import event_abi_queries

if typing.TYPE_CHECKING:
    from typing_extensions import Literal

    EventABIList = typing.Sequence[spec.EventABI]
    EventABIMap = typing.Mapping[str, spec.EventABI]
    ColumnPrefixType = Literal['arg', 'event_name', 'event_hash']


async def async_decode_events_dataframe(
    events: spec.DataFrame,
    event_abis: EventABIList | EventABIMap | None = None,
    *,
    context: spec.Context,
    column_prefix_type: ColumnPrefixType | None = None,
    column_prefix: str | None = None,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    integer_output_format: spec.IntegerOutputFormat | None = None,
    convert_invalid_str_to_none: bool = False,
    convert_invalid_str_to: None | str = None,
) -> spec.DataFrame:
    """decode a dataframe that contains raw logs

    TODO: specifically handle logs that do not provide event topics

    columns are prefixed according to input settings
    - column_prefix_type == 'arg' --> use 'arg__' as prefix
    - column_prefix_type == 'event_name' --> use '{event_name}__' as prefix
    - column_prefix_type == 'event_hash' --> use '{event_hash}__' as prefix
    - column_prefix_type == None --> use column_prefix if not None, otherwise ''
    """

    import polars as pl
    from ctc.toolbox import pl_utils

    # handle case of no events
    if len(events) == 0:
        _, df_schema, _ = _create_event_arg_schema(
            event_abis=event_abis,
            column_prefix_type=column_prefix_type,
            column_prefix=column_prefix,
            integer_output_format=integer_output_format,
        )
        arg_df = pl.DataFrame(schema=df_schema)  # type: ignore
        return pl.concat([events, arg_df], how='horizontal')

    # get event abis
    event_abis = await _async_get_events_abis(
        events=events, event_abis=event_abis, context=context
    )

    # create dataframe schema
    event_schemas, df_schema, event_hash_offsets = _create_event_arg_schema(
        event_abis=event_abis,
        column_prefix_type=column_prefix_type,
        column_prefix=column_prefix,
        integer_output_format=integer_output_format,
    )

    # create iterators for relevant columns
    n_decode_topics = max(
        len(event_schema['indexed_types'])
        for event_schema in event_schemas.values()
    )
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
    decode_unindexed = any(
        len(event_schema['unindexed_types']) > 0
        for event_schema in event_schemas.values()
    )
    if decode_unindexed:
        unindexed = events['unindexed'].to_list()
    topic_iterators = [topic1, topic2, topic3]

    # decode
    decoded_events: typing.Sequence[typing.MutableSequence[typing.Any]]
    decoded_events = [[] for i in range(len(df_schema))]
    for e, event_hash in enumerate(events['event_hash'].to_list()):
        i = event_hash_offsets[event_hash]
        event_schema = event_schemas[event_hash]

        for c in range(i):
            decoded_events[c].append(None)

        # decode indexed data
        for indexed_type, indexed_name, topic_iterator in zip(
            event_schema['indexed_types'],
            event_schema['indexed_names'],
            topic_iterators,
        ):
            if topic_iterator is None:
                raise Exception('topic_iterator not set')
            if (
                indexed_type in ['bytes', 'string']
                or indexed_type.endswith(']')
                or indexed_type.endswith(')')
            ):
                value = topic_iterator[e]
            else:
                raw_value = topic_iterator[e]
                if raw_value is not None:
                    value = abi_coding_utils.abi_decode(
                        topic_iterator[e],
                        indexed_type,
                        convert_invalid_str_to=convert_invalid_str_to,
                        convert_invalid_str_to_none=convert_invalid_str_to_none,
                    )
                else:
                    value = raw_value
            decoded_events[i].append(value)
            i = i + 1

        # decode unindexed data
        if len(event_schema['unindexed_types']) > 0:
            # unindexed_decoded = abi_coding_utils.abi_decode(
            #     unindexed[e],
            #     event_schema['unindexed_types'],
            #     convert_invalid_str_to=convert_invalid_str_to,
            #     convert_invalid_str_to_none=convert_invalid_str_to_none,
            # )
            if len(event_schema['unindexed_types']) == 1:
                result = abi_coding_utils.abi_decode(
                    unindexed[e],
                    event_schema['unindexed_types'][0],
                    convert_invalid_str_to=convert_invalid_str_to,
                    convert_invalid_str_to_none=convert_invalid_str_to_none,
                )
                unindexed_decoded = [result]
            else:
                unindexed_decoded = abi_coding_utils.abi_decode(
                    unindexed[e],
                    event_schema['unindexed_types'],
                    convert_invalid_str_to=convert_invalid_str_to,
                    convert_invalid_str_to_none=convert_invalid_str_to_none,
                )
            for value in unindexed_decoded:
                decoded_events[i].append(value)
                i = i + 1

        for c in range(i, len(df_schema)):
            decoded_events[c].append(None)

    # convert decimals (can remove if polars allows direct creation in future)
    new_columns = []
    for column, (column_name, dtype) in zip(decoded_events, df_schema):
        if dtype == pl.Decimal:
            import decimal

            new_columns.append([decimal.Decimal(value) for value in column])
        else:
            new_columns.append(column)
    decoded_events = new_columns

    # convert to dataframe
    decoded = pl.DataFrame(decoded_events, schema=df_schema, orient='col')  # type: ignore

    # convert binary columns to hex
    if binary_output_format == 'prefix_hex':
        decoded = pl_utils.binary_columns_to_prefix_hex(decoded)

    return decoded


def _create_event_arg_schema(
    *,
    event_abis: EventABIList | EventABIMap | None = None,
    column_prefix_type: ColumnPrefixType | None = None,
    column_prefix: str | None = None,
    integer_output_format: spec.IntegerOutputFormat | None = None,
) -> tuple[
    typing.Mapping[str, spec.EventSchema],
    typing.Sequence[tuple[str, spec.IntegerOutputFormat]],
    typing.Mapping[str, int],
]:
    """does not take binary_output_format into account, that happens later"""

    # format event_abi's as dict
    if not isinstance(event_abis, dict):
        if isinstance(event_abis, (list, tuple)):
            event_abis = {
                event_abi_parsing.get_event_hash(event_abi): event_abi
                for event_abi in event_abis
            }
        elif event_abis is None:
            event_abis = {}
        else:
            raise Exception('unknown events format')

    # get event schemas
    event_schemas: typing.Mapping[str, spec.EventSchema] = {
        event_hash: event_abi_parsing.get_event_schema(event_abi)
        for event_hash, event_abi in event_abis.items()
    }

    # get column prefix
    if column_prefix_type is None and column_prefix is None:
        if len(event_abis) == 1:
            column_prefix_type = 'arg'
        else:
            event_names = {
                abi.get('name')
                for abi in event_abis.values()
                if abi.get('name') is not None
            }
            if len(event_names) == len(event_abis):
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

    # create dataframe schema
    df_schema = []
    used_names = []
    offsets = [0]
    for event_hash in event_schemas.keys():
        event_schema = event_schemas[event_hash]
        if '{event_name}' in column_prefix:
            if 'name' in event_abis[event_hash]:
                event_name = event_abis[event_hash]['name']
            else:
                raise Exception('event name not specified in event abi')
            used_column_prefix = column_prefix.format(
                event_hash=event_hash,
                event_name=event_name,
            )
        else:
            used_column_prefix = column_prefix.format(event_hash=event_hash)
        for abi_type, name in zip(event_schema['types'], event_schema['names']):
            pl_type = _abi_type_to_polars_dtype(
                abi_type=abi_type,
                name=name,
                integer_output_format=integer_output_format,
            )
            name = used_column_prefix + name
            if name in used_names:
                raise Exception('naming conflict ' + str(name))

            df_schema.append((name, pl_type))
            used_names.append(name)
        offsets.append(len(df_schema))
    event_hash_offsets = dict(zip(event_schemas.keys(), offsets))

    return event_schemas, df_schema, event_hash_offsets


async def _async_get_events_abis(
    events: spec.DataFrame,
    event_abis: EventABIList | EventABIMap | None = None,
    *,
    context: spec.Context,
) -> typing.Mapping[str, spec.EventABI]:
    import polars as pl

    # package input abi's
    if isinstance(event_abis, dict):
        abis: typing.MutableMapping[str, spec.EventABI] = event_abis
    elif event_abis is None:
        abis = {}
    elif isinstance(event_abis, list):
        abis = {}
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

    return abis


def _abi_type_to_polars_dtype(
    *,
    abi_type: str,
    name: str,
    integer_output_format: spec.IntegerOutputFormat | None = None,
) -> type[object]:
    import polars as pl

    if (
        abi_type.startswith('int') or abi_type.startswith('uint')
    ) and integer_output_format is not None:
        # if a dict, using integer_output_format is optional. otherwise must use
        if isinstance(integer_output_format, dict):
            if name in integer_output_format:
                return integer_output_format[name]  # type: ignore
        else:
            if integer_output_format in [int, 'integer']:
                return int
            elif integer_output_format in [object, 'object']:
                return pl.Object
            elif integer_output_format in [float, 'float']:
                return pl.Float64
            elif isinstance(integer_output_format, pl.datatypes.DataTypeClass):
                return integer_output_format
            elif (
                integer_output_format == 'decimal'
                or str(type(integer_output_format)) == "<class 'decimal.Decimal'>"
            ):
                return pl.Decimal
            else:
                raise Exception(
                    'invalid integer_output_format: ' + str(integer_output_format)
                )

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

