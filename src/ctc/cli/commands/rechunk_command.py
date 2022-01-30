import asyncio

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': rechunk_command,
        'args': [
            {'name': 'contract_address', 'nargs': '?'},
            {'name': 'event', 'nargs': '?'},
            {'name': '--network'},
            {'name': '--all_events', 'action': 'store_true'},
            {'name': '--start_block', 'type': int},
            {'name': '--end_block', 'type': int},
            {'name': '--n_chunks', 'type': int},
            {'name': '--chunk_target_bytes', 'type': float},
            {'name': '--dry', 'action': 'store_true'},
            {'name': '--verbose', 'action': 'store_true'},
        ],
    }


def rechunk_command(
    contract_address,
    event,
    all_events,
    start_block,
    end_block,
    n_chunks,
    chunk_target_bytes,
    dry,
    verbose,
    network,
):
    coroutine = run(
        contract_address=contract_address,
        event=event,
        all_events=all_events,
        start_block=start_block,
        end_block=end_block,
        n_chunks=n_chunks,
        chunk_target_bytes=chunk_target_bytes,
        dry=dry,
        verbose=verbose,
        network=network,
    )
    asyncio.run(coroutine)


async def run(
    contract_address,
    event,
    all_events,
    start_block,
    end_block,
    n_chunks,
    chunk_target_bytes,
    dry,
    verbose,
    network,
):

    if all_events:

        await evm.async_rechunk_all(
            network=network,
            start_block=start_block,
            end_block=end_block,
            chunk_target_bytes=chunk_target_bytes,
            dry=dry,
            verbose=verbose,
        )

    elif contract_address is not None and event is not None:

        if evm.is_event_hash(event):
            event_name = event
            event_hash = None
        else:
            event_name = None
            event_hash = event

        await evm.async_rechunk_events(
            contract_address=contract_address,
            network=network,
            event_name=event_name,
            event_hash=event_hash,
            start_block=start_block,
            end_block=end_block,
            n_chunks=n_chunks,
            chunk_target_bytes=chunk_target_bytes,
            dry=dry,
            verbose=verbose,
        )

    await rpc.async_close_http_session()

