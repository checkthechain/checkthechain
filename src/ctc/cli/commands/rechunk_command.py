import asyncio

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': rechunk_command,
        'args': [
            {'name': 'contract_address', 'kwargs': {'nargs': '?'}},
            {'name': 'event', 'kwargs': {'nargs': '?', 'default': None}},
            {'name': '--network'},
            {
                'name': '--all',
                'kwargs': {'action': 'store_true', 'dest': 'all_events'},
            },
            {'name': '--start_block', 'kwargs': {'type': int}},
            {'name': '--end_block', 'kwargs': {'type': int}},
            {'name': '--n_chunks', 'kwargs': {'type': int}},
            {
                'name': '--chunk_target_bytes',
                'kwargs': {'type': float, 'required': True},
            },
            {'name': '--dry', 'kwargs': {'action': 'store_true'}},
            {'name': '--verbose', 'kwargs': {'action': 'store_true'}},
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

        await evm.async_rechunk_all_events(
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

    else:
        raise Exception(
            'usage either `ctc rechunk --all` or `ctc rechunk contract_address event_hash`'
        )

    await rpc.async_close_http_session()

