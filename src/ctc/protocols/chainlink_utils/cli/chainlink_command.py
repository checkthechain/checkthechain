import toolstr

from ctc import directory
from ctc import evm
from ctc import rpc
from ctc.cli import cli_utils
from ctc.protocols import chainlink_utils


def get_command_spec():
    return {
        'f': async_chainlink_command,
        'args': [
            {'name': 'feed', 'kwargs': {'nargs': '+'}},
            {'name': '--blocks', 'kwargs': {'nargs': '+'}},
            {'name': '--output', 'kwargs': {'default': 'stdout'}},
            {'name': '--overwrite', 'kwargs': {}},
            {'name': '--provider', 'kwargs': {}},
            {'name': '--all-fields', 'kwargs': {'action': 'store_true'}},
            # {'name': '--no-interpolate', 'kwargs': {}},
        ],
    }


async def async_chainlink_command(feed, blocks, output, overwrite, provider, all_fields):

    feed = '_'.join(feed)

    if all_fields:
        fields = 'full'
    else:
        fields = 'answer'

    if blocks is None:
        await chainlink_utils.async_summarize_feed(feed=feed)
    else:
        if evm.is_address_str(feed):
            feed_address = feed
        elif isinstance(feed, str):
            feed_address = directory.get_oracle_address(
                name=feed, protocol='chainlink'
            )
        else:
            raise Exception('unknown feed specification: ' + str(feed))
        name = await rpc.async_eth_call(feed_address, function_name='description')
        toolstr.print_text_box('Chainlink Feed: ' + name)
        print('- feed address')
        print('- feed:', feed)
        print('- fields:', fields)
        print('- output:', output)

        # if cli_utils.is_block_range(blocks):
        #     start_block, end_block = await cli_utils.async_resolve_block_range(blocks)
        #     block_kwargs = {'start_block': start_block, 'end_block': end_block}
        #     print('- block_range: [' + str(start_block) + ', ' + str(end_block) + ']')
        # else:
        resolved_blocks = await cli_utils.async_resolve_block_sample(blocks)
        block_kwargs = {'blocks': resolved_blocks}
        print('- n_blocks:', len(resolved_blocks))
        print('- min_block:', min(resolved_blocks))
        print('- max_block:', max(resolved_blocks))

        print()

        feed_data = await chainlink_utils.async_get_feed_data(
            feed,
            provider=provider,
            fields=fields,
            **block_kwargs,
        )
        df = feed_data

        cli_utils.output_data(df, output=output, overwrite=overwrite)

    await rpc.async_close_http_session()

