"""
# `ctc export <export> [options]`

The `export` command can export a variety of data types into a variety of formats

## Contents
- [Export Types](#export-types)
- [Export Options](#export-options)
- [Export Examples](#export-examples)


## Export Types

There are three main types of exports:
- `Metric Exports`: exported over any arbitrary list of blocks
    - derived mostly from blockwise rpc methods
    - example: oracle prices
- `Event Exports`: exported over a range of blocks
    - derived mostly from events
    - example: individual DEX trades
- `Snapshot Exports`: exports multiple datapoints within a single block
    - example: ERC20 holdings of multiple wallets

#### Metric Export Types
- events {<event_hash> | <event_name>} [<topic_name>=<topic_value]*
- erc20 transfers {<token_address> | <token_symbol>}
- uniswap {swaps | mints | burns} {<pool_address>}

#### Event Export Types
- calls {<call_data> | (<function_name> [<function_parameters>]})
- eth_balance <address>
- block <block_attribute>
- erc20 {total-supply | balance-of | allowance} {<token_address> | <token_symbol>} [<address>]
- chainlink {<feed_address> | <feed_name>}
- uniswap {price | volume | depth} {<pool_address>}

#### Snapshot Export Types
- erc20 balance-of {<token_address> | <token_symbol>} [<addresses>]


## Export Options

#### Provider Options
--network: name or id of network

#### Metric Export Options
--blocks: comma-separated list of blocks

#### Event Export Options
--start-block: initial block for data range
--end-block: final block for data range

#### Snapshot Export Options
--block: block to use for snapshot

#### Output Options
--output <filepath>: output to a file instead of stdout, should be csv or json
--overwrite: allows output file to be overwitten if it already exists


## Export Examples
"""

import os

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': export_command,
        'args': [
            {'name': 'export_args', 'kwargs': {'nargs': '+'}},
            {'name': '--start-block', 'kwargs': {'type': int}},
            {'name': '--end-block', 'kwargs': {'type': int}},
            {'name': '--output'},
            {'name': '--network'},
            {'name': '--overwrite', 'kwargs': {'action': 'store_true'}},
            # {'name': '--exclude-columns', 'kwargs': {'help': 'columns to exclude'}},
            # {'name': '--include-columns', 'kwargs': {'help': 'columns to include'}},
        ],
    }


async def export_command(
    export_args, start_block, end_block, output, network, overwrite
):
    print(export_args, start_block, end_block, output)

    export_type = export_args[0]
    tail = export_args[1:]

    provider = {'network': network}

    if export_type == 'events':
        if len(tail) != 2:
            raise Exception('must specify contract and event')
        contract_address, event = tail

        kwargs = {}
        if event.startswith('0x') and len(event) == 66:
            kwargs['event_hash'] = event
        else:
            kwargs['event_name'] = event

        df = await evm.async_get_events(
            contract_address=contract_address,
            start_block=start_block,
            end_block=end_block,
            provider=provider,
            **kwargs,
        )

        await rpc.async_close_http_session()

    elif export_type == 'calls':

        # get call data
        contract_address, *call_data = tail
        if len(call_data) == 1 and call_data.startswith('0x'):
            kwargs = {'call_data': call_data}
        else:
            kwargs = {
                'function_name': function_name,
                'function_parameters': function_parameters,
            }

        # get blocks
        if blocks is not None:
            block_numbers = [int(item) for item in blocks.split(',')]
        else:
            if start_block is None:
                start_block = await evm.async_get_contract_creation_block(
                    contract_address
                )
            if end_block is None:
                end_block = 'latest'
            end_block = await evm.async_block_reference_to_int(end_block)
            block_numbers = list(range(start_block, end_block + 1))

        df = await rpc.batch_eth_call(
            to_address=contract_address,
            block_numbers=block_numbers,
            provider=provider,
            **kwargs,
        )

    elif export_type == 'chainlink':
        pass

    elif export_type.startswith('erc20'):
        pass

    else:
        raise Exception('unknown export type: ' + str(export_type))

    # output result
    if output is None or output == 'stdout':
        print(df)

    else:

        # check whether can overwrite file
        if os.path.isfile(output):
            if overwrite:
                pass
            elif toolcli.input_yes_or_no('File already exists. Overwrite? '):
                pass
            else:
                raise Exception('aborting')

        elif output.endswith('.csv'):
            df.to_csv(output)

        elif output.endswith('.json'):
            pass

        else:
            raise Exception()

