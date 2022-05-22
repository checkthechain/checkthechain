from __future__ import annotations

import typing

import toolcli

from ctc import evm
from ctc import spec
from ctc.cli import cli_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_events_command,
        'help': 'get contract events',
        'args': [
            {
                'name': 'contract',
                'help': 'contract address of event',
            },
            {
                'name': 'event',
                'help': 'event name or event hash',
            },
            {
                'name': '--blocks',
                'help': 'block range',
                'nargs': '+',
            },
            {
                'name': '--output',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {
                'name': '--verbose',
                'help': 'display more event data',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca Transfer',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca Transfer --blocks [14000000, 14100000]',
        ],
    }


async def async_events_command(
    contract: str,
    event: str,
    blocks: typing.Sequence[str],
    output: str,
    overwrite: bool,
    verbose: bool,
) -> None:

    if blocks is not None:
        all_blocks = await cli_utils.async_resolve_block_range(blocks)
        start_block = all_blocks[0]
        end_block = all_blocks[-1]
    else:
        start_block = None
        end_block = None

    if event.startswith('0x'):
        events: spec.DataFrame = await evm.async_get_events(
            contract_address=contract,
            start_block=start_block,
            end_block=end_block,
            verbose=False,
            event_hash=event,
        )
    else:
        events = await evm.async_get_events(
            contract_address=contract,
            start_block=start_block,
            end_block=end_block,
            verbose=False,
            event_name=event,
        )

    if len(events) == 0:
        print('[no events found]')

    else:

        # output
        if not verbose:
            events.index = typing.cast(
                spec.PandasIndex,
                [
                    str(value)
                    for value in events.index.get_level_values('block_number')
                ]
            )
            events.index.name = 'block'
            events = events[
                [column for column in events.columns if column.startswith('arg__')]
            ]
            new_column_names = {
                old_column: old_column[5:]
                for old_column in events.columns
            }
            events = events.rename(columns=new_column_names)
        cli_utils.output_data(events, output=output, overwrite=overwrite)
