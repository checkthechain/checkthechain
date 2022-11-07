from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import block_utils
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
    decode: bool = True,
    multiindex: bool = True,
    share_abis_across_contracts: bool = True,
    include_timestamps: bool = False,
    include_event_names: bool = False,
    output_format: Literal['dataframe', 'dict'] = 'dataframe',
) -> spec.DataFrame:
    """get events"""

    from . import event_hybrid_queries
    from . import event_node_utils
    from . import event_query_utils
    from . import event_metadata

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
        network=network,
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
        n_contracts = len(set(df['contract_address'].values))
        cli.print_bullet(key='n_contracts', value=n_contracts)
        n_event_types = len(set(df['event_hash'].values))
        cli.print_bullet(key='n_event_types', value=n_event_types)

    # set index
    if multiindex:
        index_fields = [
            'block_number',
            'transaction_index',
            'log_index',
        ]
        df = df.set_index(index_fields)
    else:
        df.index = df.index.get_level_values('block_number')

    # insert metadata columns
    if include_timestamps:
        timestamps = await event_metadata.async_get_event_timestamps(
            df,
            provider=provider,
        )
        df.insert(0, 'timestamp', timestamps)  # type: ignore
    if include_event_names:
        df['event_name'] = event_metadata._async_get_event_names_column(
            events=df,
            share_abis_across_contracts=share_abis_across_contracts,
        )

    # format data
    if decode:

        if event_abi is not None:
            event_abis: typing.Mapping[
                str | tuple[str, str], spec.EventABI
            ] | None
            event_abis = {abi_utils.get_event_hash(event_abi): event_abi}
        else:
            event_abis = None
        df = await abi_utils.async_decode_events_dataframe(
            df,
            event_abis=event_abis,
            decode_metadata=False,
            output_format=output_format,
            share_abis_across_contracts=share_abis_across_contracts,
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
