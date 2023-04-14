from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import block_utils
from .. import contract_utils
from . import event_metadata
from . import event_query_utils

if typing.TYPE_CHECKING:
    import tooltime

    from typing_extensions import Literal


async def async_get_events(
    contract_address: spec.Address | None = None,
    *,
    event_name: str | None = None,
    event_abi: spec.EventABI | None = None,
    event_hash: str | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    context: spec.Context = None,
    named_topics: typing.Mapping[str, typing.Any] | None = None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
    topic1_is_binary: bool | None = None,
    topic2_is_binary: bool | None = None,
    topic3_is_binary: bool | None = None,
    verbose: int | bool = 1,
    decode: bool = True,
    share_abis_across_contracts: bool = True,
    include_timestamps: bool = False,
    include_event_names: bool = False,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    integer_output_format: spec.IntegerOutputFormat | None = None,
    only_columns: typing.Sequence[str] | None = None,
    exclude_columns: typing.Sequence[str] | None = None,
    convert_ints: type | bool = False,
    convert_invalid_str_to_none: bool = False,
    convert_invalid_str_to: None | str = None,
    max_blocks_per_request: int = 2000,
) -> spec.DataFrame:
    """get events"""

    from . import event_hybrid_queries

    # get query inputs
    (
        start_block,
        end_block,
        encoded_topics,
        event_abi,
        columns_to_load,
    ) = await _async_get_query_inputs(
        contract_address=contract_address,
        event_name=event_name,
        event_abi=event_abi,
        event_hash=event_hash,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        context=context,
        named_topics=named_topics,
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
        topic1_is_binary=topic1_is_binary,
        topic2_is_binary=topic2_is_binary,
        topic3_is_binary=topic3_is_binary,
        decode=decode,
        only_columns=only_columns,
        exclude_columns=exclude_columns,
        include_event_names=include_event_names,
    )

    # query data from db and/or node
    df = await event_hybrid_queries._async_query_events_from_node_and_db(
        contract_address=contract_address,
        event_hash=encoded_topics[0],
        topic1=encoded_topics[1],
        topic2=encoded_topics[2],
        topic3=encoded_topics[3],
        start_block=start_block,
        end_block=end_block,
        verbose=verbose,
        binary_output_format=binary_output_format,
        columns_to_load=columns_to_load,
        context=context,
        max_blocks_per_request=max_blocks_per_request,
    )

    # post-process result
    return await _async_postprocess_query_result(
        df=df,
        event_abi=event_abi,
        verbose=bool(verbose),
        columns_to_load=columns_to_load,
        decode=decode,
        context=context,
        share_abis_across_contracts=share_abis_across_contracts,
        include_timestamps=include_timestamps,
        include_event_names=include_event_names,
        binary_output_format=binary_output_format,
        integer_output_format=integer_output_format,
        convert_invalid_str_to_none=convert_invalid_str_to_none,
        convert_invalid_str_to=convert_invalid_str_to,
        convert_ints=convert_ints,
    )


async def _async_postprocess_query_result(
    *,
    df: spec.DataFrame,
    event_abi: spec.EventABI | None,
    verbose: bool,
    columns_to_load: typing.Sequence[str],
    decode: bool = True,
    context: spec.Context,
    share_abis_across_contracts: bool = True,
    include_timestamps: bool = False,
    include_event_names: bool = False,
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    integer_output_format: spec.IntegerOutputFormat | None = None,
    convert_invalid_str_to_none: bool = False,
    convert_invalid_str_to: None | str = None,
    convert_ints: type | bool = False,
) -> spec.DataFrame:

    import polars as pl

    # summarize output
    if verbose >= 2:
        from ctc import cli

        print()
        print('events gathered')
        cli.print_bullet(key='n_events', value=len(df))
        if 'contract_address' in columns_to_load:
            n_contracts = df['contract_address'].n_unique()
            cli.print_bullet(key='n_contracts', value=n_contracts)
        if 'event_hash' in columns_to_load:
            n_event_types = df['event_hash'].n_unique()
            cli.print_bullet(key='n_event_types', value=n_event_types)

    # insert metadata columns
    if include_timestamps:

        timestamps = await event_metadata.async_get_event_timestamps(
            df,
            context=context,
        )
        df = df.with_columns(pl.Series(name='timestamp', values=timestamps))
    if include_event_names:
        event_names = await event_metadata._async_get_event_names_column(
            events=df,
            share_abis_across_contracts=share_abis_across_contracts,
            context=context,
        )
        df = df.with_columns(pl.Series(name='event_name', values=event_names))

    # format data
    if decode:
        decoded = await abi_utils.async_decode_events_dataframe(
            df,
            event_abis=([event_abi] if event_abi is not None else None),
            context=context,
            binary_output_format=binary_output_format,
            integer_output_format=integer_output_format,
            convert_invalid_str_to_none=convert_invalid_str_to_none,
            convert_invalid_str_to=convert_invalid_str_to,
        )
        df = df.with_columns(decoded)
        encoded_columns = ['topic1', 'topic2', 'topic3', 'unindexed']
        to_drop = [column for column in encoded_columns if column in df]
        df = df.drop(to_drop)

    if convert_ints:
        int_columns = df.select(pl.col(pl.Object)).columns
        if isinstance(convert_ints, bool):
            import numpy as np

            converted = []
            for column in int_columns:
                as_array = np.array(df[column].to_list())
                max_value = as_array.max()
                min_value = as_array.min()
                if max_value > 2 ** 32 - 1 and min_value < 2 ** 32 + 1:
                    as_array = as_array.astype(float)
                    dtype: pl.datatypes.DataTypeClass = pl.Float64
                else:
                    dtype = pl.Int64
                converted.append(pl.Series(column, as_array, dtype=dtype))
            df = df.with_columns(converted)
        elif isinstance(convert_ints, pl.datatypes.DataTypeClass):
            converted = []
            for column in int_columns:
                new_column = pl.Series(column, df[column].to_list(), dtype=convert_ints)
                converted.append(new_column)
            df = df.with_columns(converted)
        elif isinstance(convert_ints, type):
            return_dtypes = {
                int: pl.datatypes.Int64,
                float: pl.datatypes.Float64,
            }
            return_dtype = return_dtypes.get(convert_ints)
            converted = [
                df[column].apply(convert_ints, return_dtype=return_dtype)
                for column in int_columns
            ]
            df = df.with_columns(converted)
        else:
            raise Exception('unknown format for convert ints')

    return df


async def _async_get_query_inputs(
    contract_address: spec.Address | None = None,
    *,
    event_name: str | None = None,
    event_abi: spec.EventABI | None = None,
    event_hash: str | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    context: spec.Context = None,
    named_topics: typing.Mapping[str, typing.Any] | None = None,
    topic1: typing.Any | None = None,
    topic2: typing.Any | None = None,
    topic3: typing.Any | None = None,
    topic1_is_binary: bool | None = None,
    topic2_is_binary: bool | None = None,
    topic3_is_binary: bool | None = None,
    decode: bool = True,
    only_columns: typing.Sequence[str] | None = None,
    exclude_columns: typing.Sequence[str] | None = None,
    include_event_names: bool = False,
) -> tuple[
    int, int, typing.Sequence[bytes | None], spec.EventABI | None, typing.Sequence[str]
]:

    # determine start and end block
    start_block, end_block = await block_utils.async_resolve_block_range(
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        allow_none=True,
        to_int=True,
        end_none_means='latest',
        context=context,
    )
    if start_block is None:
        if contract_address is None:
            raise Exception('must specify contract_address or start_block')
        start_block = await contract_utils.async_get_contract_creation_block(
            contract_address=contract_address,
            context=context,
        )
    if start_block is None:
        raise Exception('could not determine start_block')
    if end_block is None:
        raise Exception('could not determine end_block')

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
        topic1=topic1,
        topic2=topic2,
        topic3=topic3,
        topic1_is_binary=topic1_is_binary,
        topic2_is_binary=topic2_is_binary,
        topic3_is_binary=topic3_is_binary,
        context=context,
    )

    # compute which columns to return
    columns_to_load = _get_columns_to_load(
        decode=decode,
        event_abi=event_abi,
        only_columns=only_columns,
        exclude_columns=exclude_columns,
        include_event_names=include_event_names,
    )

    return (
        start_block,
        end_block,
        encoded_topics,
        event_abi,
        columns_to_load,
    )


def _get_columns_to_load(
    *,
    only_columns: typing.Sequence[str] | None,
    exclude_columns: typing.Sequence[str] | None,
    decode: bool,
    event_abi: spec.EventABI | None,
    include_event_names: bool,
) -> typing.Sequence[str]:
    """specify which columns to use for partial loading

    need to account for dependencies
    - .e.g. if want to decode an indexed topic, need to load raw binary column
    """

    if only_columns is None and exclude_columns is None:
        exclude_columns = []
    if only_columns is not None and exclude_columns is not None:
        raise Exception('can only specify only_columns or exclude_columns')

    def adding(column: str) -> bool:
        return (only_columns is not None and column in only_columns) or (
            exclude_columns is not None and column not in exclude_columns
        )

    # index columns
    columns = []
    for column in [
        'block_number',
        'transaction_index',
        'log_index',
        'transaction_hash',
        'contract_address',
        'event_hash',
    ]:
        if adding(column):
            columns.append(column)

    if decode:
        # fetch topic and data columns if need to decode topics

        if event_abi is None:
            for column in ['topic1', 'topic2', 'topic3', 'unindexed']:
                if adding(column):
                    columns.append(column)

        else:

            # indexed names
            indexed = abi_utils.get_event_indexed_names(event_abi)
            n_indexed = len(indexed)
            if n_indexed >= 1:
                name = 'arg__' + indexed[0]
                if adding(name):
                    columns.append('topic1')
            if n_indexed >= 2:
                name = 'arg__' + indexed[1]
                if adding(name):
                    columns.append('topic2')
            if n_indexed >= 3:
                name = 'arg__' + indexed[2]
                if adding(name):
                    columns.append('topic3')

            # unindexed names
            unindexed = abi_utils.get_event_unindexed_names(event_abi)
            if any(adding('arg__' + name) for name in unindexed):
                columns.append('unindexed')

    else:
        # fetch topic and data columns if emitted by abi

        if event_abi is not None:
            n_indexed = len(abi_utils.get_event_indexed_names(event_abi))
            n_unindexed = len(abi_utils.get_event_unindexed_names(event_abi))
        else:
            n_indexed = 3
            n_unindexed = 1

        if n_indexed >= 1 and adding('topic1'):
            columns.append('topic1')
        if n_indexed >= 2 and adding('topic2'):
            columns.append('topic2')
        if n_indexed >= 3 and adding('topic3'):
            columns.append('topic3')
        if n_unindexed >= 1 and adding('unindexed'):
            columns.append('unindexed')

    # validate
    if only_columns is not None:

        # control specialty columns elsewhere
        if 'timestamp' in only_columns:
            raise Exception(
                'use include_timestamps to include/exclude timestamp'
            )
        if 'event_name' in only_columns:
            raise Exception(
                'use include_event_names to include/exclude timestamp'
            )
        for column in columns:
            if column in {
                'block_number',
                'transaction_index',
                'log_index',
            }:
                # ok, this is expected
                pass
            elif column not in only_columns:
                if column.startswith('arg__') and not decode:
                    message = 'cannot include arg__ columns when decode=False'
                elif (
                    column in {'topic1', 'topic2', 'topic3', 'unindexed'}
                    and decode
                ):
                    continue
                else:
                    message = 'cannot include column: ' + str(column)
                raise Exception(message)
    if exclude_columns is not None:
        if 'timestamp' in exclude_columns:
            raise Exception(
                'use include_timestamps to include/exclude timestamp'
            )
        if 'event_name' in exclude_columns:
            raise Exception(
                'use include_event_names to include/exclude timestamp'
            )
        for column in exclude_columns:
            if column in columns:
                if column == 'block_number':
                    message = 'cannot exclude block_number'
                else:
                    message = 'cannot exclude column: ' + str(column)
                raise Exception(message)
    if include_event_names and (
        'event_hash' not in columns or 'contract_address' not in columns
    ):
        raise Exception(
            'must load event_hash and contract_address to load event names'
        )

    return columns

