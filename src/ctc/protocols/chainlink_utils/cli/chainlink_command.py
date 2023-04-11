from __future__ import annotations

import time
import typing

import toolcli
import toolstr
import tooltime

from ctc import config
from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.cli import cli_utils
from ctc.protocols import chainlink_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chainlink_command,
        'help': 'output Chainlink feed data',
        'args': [
            {'name': 'feed', 'nargs': '+', 'help': 'name or address of feed'},
            {
                'name': ['--verbose', '-v'],
                'help': 'show additional information',
                'action': 'store_true',
            },
            {
                'name': '--blocks',
                'help': 'block range of datapoints',
            },
            {
                'name': '--time',
                'dest': 'timelength',
                'help': 'historical duration to show feed data',
            },
            {
                'name': '--export',
                'default': 'stdout',
                'help': 'file path for output (.json or .csv)',
            },
            {
                'name': '--overwrite',
                'action': 'store_true',
                'help': 'specify that output path can be overwritten',
            },
            {'name': '--provider', 'help': 'rpc provider name or url'},
            {'name': '--network', 'help': 'network name or chain_id'},
            {
                'name': '--all-fields',
                'action': 'store_true',
                'help': 'include all output fields',
            },
            {
                'name': '--interpolate',
                'help': 'interpolate all blocks in range',
                'action': 'store_true',
            },
        ],
        'examples': [
            'DAI_USD',
            '0xaed0c38402a5d19df6e4c03f4e2dced6e29c1ee9',
            'DAI_USD --blocks 14000000:14001000',
        ],
    }


async def async_chainlink_command(
    *,
    feed: typing.Sequence[str],
    verbose: bool,
    blocks: str | None,
    timelength: str,
    export: str,
    overwrite: bool,
    provider: str | None,
    network: spec.NetworkReference | None,
    all_fields: bool | None,
    interpolate: bool,
) -> None:

    context = config.create_user_input_context(
        provider=provider,
        network=network,
    )

    feed_str = '_'.join(feed)

    feed_str = await evm.async_resolve_address(feed_str, context=context)

    if timelength is not None:
        timelength_seconds = tooltime.timelength_to_seconds(timelength)
        start_block: int | None = await evm.async_get_block_of_timestamp(
            time.time() - timelength_seconds,
            mode='<=',
            context=context,
        )
    else:
        start_block = None

    if all_fields:
        fields: typing.Literal['full', 'answer'] = 'full'
    else:
        fields = 'answer'

    if blocks is None:
        await chainlink_utils.async_print_feed_summary(
            feed=feed_str,
            verbose=verbose,
            start_block=start_block,
            context=context,
        )
    else:
        feed_address = await chainlink_utils.async_resolve_feed_address(
            feed=feed_str,
            context=context,
        )
        name = await rpc.async_eth_call(
            feed_address,
            function_abi=chainlink_utils.feed_function_abis['description'],
            context=context,
        )
        toolstr.print_text_box('Chainlink Feed: ' + name)
        print('- feed address')
        print('- feed:', feed_str)
        print('- fields:', fields)
        print('- output:', export)

        if blocks is not None:
            start_block, end_block = await cli_utils.async_parse_block_range(
                blocks,
                context=context,
            )
        else:
            start_block = None
            end_block = None
        # block_kwargs = {'blocks': resolved_blocks}
        # print('- n_blocks:', len(resolved_blocks))
        if start_block is not None:
            print('- start_block:', start_block)
        if end_block is not None:
            print('- end_block:', end_block)

        feed_data = await chainlink_utils.async_get_feed_data(
            feed_str,
            fields=fields,
            start_block=start_block,
            end_block=end_block,
            interpolate=interpolate,
            context=context,
        )
        df = feed_data

        print()
        cli_utils.output_data(df, output=export, overwrite=overwrite, raw=True)
