from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils


def get_command_spec():
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
    }


async def async_events_command(
    contract,
    event,
    blocks,
    output,
    overwrite,
    verbose,
):

    if event.startswith('0x'):
        kwargs = {'event_hash': event}
    else:
        kwargs = {'event_name': event}

    if blocks is not None:
        all_blocks = await cli_utils.async_resolve_block_range(blocks)
        start_block = all_blocks[0]
        end_block = all_blocks[-1]
    else:
        start_block = None
        end_block = None

    events = await evm.async_get_events(
        contract_address=contract,
        start_block=start_block,
        end_block=end_block,
        verbose=False,
        **kwargs
    )

    if len(events) == 0:
        print('[no events found]')

    else:

        # output
        if not verbose:
            events.index = [
                str(value)
                for value in events.index.get_level_values('block_number')
            ]
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

    await rpc.async_close_http_session()

