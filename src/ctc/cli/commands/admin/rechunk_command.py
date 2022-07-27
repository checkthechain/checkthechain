from __future__ import annotations

import toolcli

from ctc import evm
from ctc.evm.event_utils import event_backends
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_rechunk,
        'help': 'rechunk events by specific chunk size',
        'args': [
            {
                'name': 'contract',
                'nargs': '?',
                'help': 'address of contract emitting the event',
            },
            {
                'name': 'event',
                'nargs': '?',
                'default': None,
                'help': 'event hash',
            },
            {
                'name': '--network',
                'metavar': 'NAME_OR_ID',
                'help': 'network to rechunk events of',
            },
            {
                'name': '--all',
                'action': 'store_true',
                'dest': 'all_events',
                'help': 'whether to rechunk all events (can take a long time)',
            },
            {
                'name': '--start-block',
                'type': int,
                'help': 'start of block range to rechunk',
            },
            {
                'name': '--end-block',
                'type': int,
                'help': 'end of block range to rechunk',
            },
            {
                'name': '--chunk-bytes',
                'type': int,
                'required': True,
                'help': 'target number of bytes per chunk',
            },
            {
                'name': '--dry',
                'action': 'store_true',
                'help': 'perform a dry run where no changes are made',
            },
            {
                'name': ['--verbose', '-v'],
                'action': 'store_true',
                'help': 'increase verbosity',
            },
        ],
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
            '--all',
        ],
        'hidden': True,
    }


async def async_rechunk(
    *,
    contract: spec.Address,
    event: str,
    all_events: bool,
    start_block: int,
    end_block: int,
    chunk_bytes: int,
    dry: bool,
    verbose: bool,
    network: spec.NetworkReference,
) -> None:

    if all_events:

        await event_backends.async_rechunk_all_events(
            network=network,
            start_block=start_block,
            end_block=end_block,
            chunk_target_bytes=chunk_bytes,
            dry=dry,
            verbose=verbose,
        )

    elif contract is not None and event is not None:

        if evm.is_event_hash(event):
            event_name = event
            event_hash = None
        else:
            event_name = None
            event_hash = event

        await event_backends.async_rechunk_events(
            contract_address=contract,
            network=network,
            event_name=event_name,
            event_hash=event_hash,
            start_block=start_block,
            end_block=end_block,
            chunk_target_bytes=chunk_bytes,
            dry=dry,
            verbose=verbose,
        )

    else:
        raise Exception(
            'usage either `ctc rechunk --all` or `ctc rechunk contract_address event_hash`'
        )
