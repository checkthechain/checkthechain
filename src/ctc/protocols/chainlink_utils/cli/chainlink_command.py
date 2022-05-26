from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils
from ctc.protocols import chainlink_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chainlink_command,
        'help': 'output Chainlink feed data',
        'args': [
            {'name': 'feed', 'nargs': '+', 'help': 'name or address of feed'},
            {
                'name': '--blocks',
                'nargs': '+',
                'help': 'block range of datapoints',
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
            {'name': '--provider', 'help': 'rpc provider name or url'},
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
            {
                'name': '--shell',
                'help': 'open shell with Chainlink data',
                'action': 'store_true',
            },
        ],
    }


async def async_chainlink_command(
    feed: typing.Sequence[str],
    blocks: typing.Optional[typing.Sequence[str]],
    output: str,
    overwrite: bool,
    provider: typing.Optional[str],
    all_fields: typing.Optional[bool],
    interpolate: bool,
    shell: bool,
) -> None:

    feed_str = '_'.join(feed)

    feed_str = await evm.async_resolve_address(feed_str)

    if all_fields:
        fields: typing.Literal['full', 'answer'] = 'full'
    else:
        fields = 'answer'

    if blocks is None:
        await chainlink_utils.async_summarize_feed(feed=feed_str)
    else:
        if evm.is_address_str(feed_str):
            feed_address = feed_str
        elif isinstance(feed_str, str):
            feed_address = directory.get_oracle_address(
                name=feed_str, protocol='chainlink'
            )
        else:
            raise Exception('unknown feed specification: ' + str(feed_str))
        name = await rpc.async_eth_call(
            feed_address,
            function_abi=chainlink_utils.feed_function_abis['description'],
        )
        toolstr.print_text_box('Chainlink Feed: ' + name)
        print('- feed address')
        print('- feed:', feed_str)
        print('- fields:', fields)
        print('- output:', output)

        # if cli_utils.is_block_range(blocks):
        #     start_block, end_block = await cli_utils.async_resolve_block_range(blocks)
        #     block_kwargs = {'start_block': start_block, 'end_block': end_block}
        #     print('- block_range: [' + str(start_block) + ', ' + str(end_block) + ']')
        # else:
        if blocks is not None:
            start_block, end_block = await cli_utils.async_resolve_block_range(
                blocks
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
            provider=provider,
            fields=fields,
            start_block=start_block,
            end_block=end_block,
            interpolate=interpolate,
        )
        df = feed_data

        if shell:
            # explore more advanced functionality with https://ipython.readthedocs.io/en/stable/api/generated/IPython.terminal.embed.html
            from IPython import embed  # type: ignore
            import nest_asyncio  # type: ignore

            nest_asyncio.apply()
            print()
            embed(
                colors='neutral',
                banner1='variable `feed_data` contains the data of interest\n',
            )

            return

        print()
        cli_utils.output_data(df, output=output, overwrite=overwrite, raw=True)
