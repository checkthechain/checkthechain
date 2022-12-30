from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import block_utils
from .. import contract_utils
from .. import network_utils

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
    use_db: bool = True,
    read_from_db: bool | None = None,
    write_to_db: bool | None = None,
    context: spec.Context = None,
    named_topics: typing.Mapping[str, typing.Any] | None = None,
    decoded_topic1: typing.Any | None = None,
    decoded_topic2: typing.Any | None = None,
    decoded_topic3: typing.Any | None = None,
    encoded_topic1: spec.BinaryData | None = None,
    encoded_topic2: spec.BinaryData | None = None,
    encoded_topic3: spec.BinaryData | None = None,
    verbose: int | bool = 1,
    decode: bool = True,
    keep_multiindex: bool = True,
    share_abis_across_contracts: bool = True,
    include_timestamps: bool = False,
    include_event_names: bool = False,
    output_format: Literal['dataframe', 'dict'] = 'dataframe',
    binary_output_format: Literal['binary', 'prefix_hex'] = 'prefix_hex',
    only_columns: typing.Sequence[str] | None = None,
    exclude_columns: typing.Sequence[str] | None = None,
) -> spec.DataFrame:
    """get events"""

    from . import event_hybrid_queries
    from . import event_node_utils
    from . import event_query_utils
    from . import event_metadata

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
        allow_none=True,
        to_int=True,
        end_none_means='latest',
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
        decoded_topic1=decoded_topic1,
        decoded_topic2=decoded_topic2,
        decoded_topic3=decoded_topic3,
        encoded_topic1=encoded_topic1,
        encoded_topic2=encoded_topic2,
        encoded_topic3=encoded_topic3,
        context=context,
    )

    # compute which columns to return
    columns_to_load = _get_columns_to_load(
        decode=decode,
        event_abi=event_abi,
        only_columns=only_columns,
        exclude_columns=exclude_columns,
        keep_multiindex=keep_multiindex,
        include_event_names=include_event_names,
    )

    # query data from db and/or node
    events: typing.Union[spec.DataFrame, typing.Sequence[spec.EncodedEvent]]
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
                verbose=verbose,
                binary_output_format=binary_output_format,
                columns_to_load=columns_to_load,
                context=context,
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
            verbose=verbose,
            binary_output_format=binary_output_format,
            context=context,
        )

    # convert to dataframe as needed
    if isinstance(events, list):
        import pandas as pd

        df = pd.DataFrame(events)
    elif spec.is_dataframe(events):
        df = events
    else:
        raise Exception('unknown events format: ' + str(events))

    # summarize output
    if verbose >= 2:
        from ctc import cli

        print()
        print('events gathered')
        cli.print_bullet(key='n_events', value=len(df))
        if 'contract_address' in columns_to_load:
            n_contracts = len(set(df['contract_address'].values))
            cli.print_bullet(key='n_contracts', value=n_contracts)
        if 'event_hash' in columns_to_load:
            n_event_types = len(set(df['event_hash'].values))
            cli.print_bullet(key='n_event_types', value=n_event_types)

    # set index
    if keep_multiindex:
        index_fields = [
            'block_number',
            'transaction_index',
            'log_index',
        ]
        df = df.set_index(index_fields)
    else:
        df = df.set_index('block_number')

    # insert metadata columns
    if include_timestamps:
        timestamps = await event_metadata.async_get_event_timestamps(
            df,
            context=context,
        )
        df.insert(0, 'timestamp', timestamps)
    if include_event_names:
        df['event_name'] = await event_metadata._async_get_event_names_column(
            events=df,
            share_abis_across_contracts=share_abis_across_contracts,
            context=context,
        )

    # format data
    if decode:

        df = await abi_utils.async_decode_events_dataframe(
            df,
            decode_metadata=False,
            single_event_abi=event_abi,
            share_abis_across_contracts=share_abis_across_contracts,
            output_format=output_format,
            binary_output_format=binary_output_format,
            context=context,
        )
        return df

    else:

        # convert to output format
        if output_format == 'dataframe':
            return df
        elif output_format == 'dict':
            return df.reset_index().to_dict(orient='records')  # type: ignore
        else:
            raise Exception('unknown output format: ' + str(output_format))


def _get_columns_to_load(
    *,
    only_columns: typing.Sequence[str] | None,
    exclude_columns: typing.Sequence[str] | None,
    decode: bool,
    event_abi: spec.EventABI | None,
    keep_multiindex: bool,
    include_event_names: bool,
) -> set[str]:
    """specify which columns to use for partial loading"""

    if only_columns is None and exclude_columns is None:
        exclude_columns = []
    if only_columns is not None and exclude_columns is not None:
        raise Exception(
            'can only specify one of only_columns or exclude_columns'
        )

    # index columns
    columns = set()
    if keep_multiindex:
        columns.update({'block_number', 'transaction_index', 'log_index'})
    else:
        columns.update({'block_number'})

    # standard columns
    standard_columns = {'transaction_hash', 'contract_address', 'event_hash'}
    for column in standard_columns:
        if (only_columns is not None and column in only_columns) or (
            exclude_columns is not None and column not in exclude_columns
        ):
            columns.add(column)

    # arg columns
    if decode:

        if event_abi is None:
            columns.update({'topic1', 'topic2', 'topic3', 'unindexed'})

        else:
            # indexed names
            indexed = abi_utils.get_event_indexed_names(event_abi)
            if len(indexed) >= 1:
                name = 'arg__' + indexed[0]
                if (only_columns is not None and name in only_columns) or (
                    exclude_columns is not None and name not in exclude_columns
                ):
                    columns.add('topic1')
            if len(indexed) >= 2:
                name = 'arg__' + indexed[1]
                if (only_columns is not None and name in only_columns) or (
                    exclude_columns is not None and name not in exclude_columns
                ):
                    columns.add('topic2')
            if len(indexed) >= 3:
                name = 'arg__' + indexed[2]
                if (only_columns is not None and name in only_columns) or (
                    exclude_columns is not None and name not in exclude_columns
                ):
                    columns.add('topic3')

            # unindexed names
            unindexed = abi_utils.get_event_unindexed_names(event_abi)
            if only_columns is not None:
                if any('arg__' + name in only_columns for name in unindexed):
                    columns.add('unindexed')
            elif exclude_columns is not None:
                if any('arg__' + name not in exclude_columns for name in unindexed):
                    columns.add('unindexed')
            else:
                raise Exception('both only_columns and exclude_columns are None')

    else:

        if event_abi is not None:
            abi_has_indexed = len(abi_utils.get_event_indexed_names(event_abi))
            abi_has_unindexed = (
                len(abi_utils.get_event_unindexed_names(event_abi)) > 0
            )
        else:
            abi_has_indexed = 3
            abi_has_unindexed = True

        if only_columns is not None:
            if abi_has_indexed >= 1 and 'topic1' in only_columns:
                columns.add('topic1')
            if abi_has_indexed >= 2 and 'topic2' in only_columns:
                columns.add('topic2')
            if abi_has_indexed >= 3 and 'topic3' in only_columns:
                columns.add('topic3')
            if abi_has_unindexed and 'unindexed' in only_columns:
                columns.add('unindexed')

        elif exclude_columns is not None:
            if abi_has_indexed >= 1 and 'topic1' not in exclude_columns:
                columns.add('topic1')
            if abi_has_indexed >= 2 and 'topic2' not in exclude_columns:
                columns.add('topic2')
            if abi_has_indexed >= 3 and 'topic3' not in exclude_columns:
                columns.add('topic3')
            if abi_has_unindexed and 'unindexed' not in exclude_columns:
                columns.add('unindexed')

        else:
            raise Exception('exclude_columns should have been []')

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
                elif column in ['transaction_index', 'log_index']:
                    message = (
                        'to exclude index columns, use keep_multiindex=False'
                    )
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
