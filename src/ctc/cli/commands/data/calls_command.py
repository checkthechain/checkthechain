"""
TODO:
- allow using function selector instead of function name
- allow using quoted json to indicate function abi
- --normalize arg to normalize outputs
"""

from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import binary
from ctc import cli
from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.cli import cli_utils
from ctc.cli import cli_run

command_help = """output the result of multiple contract eth_call's

This command can be used in two ways:
[title]1) **Multi-contract Calls**[/title]: same call across multiple contracts
    - This is indicated by the `--addresses` parameter
    - Example: `call <function-name> --addresses <addr1> <addr2> <addr3>`
[title]2) **Historical Calls**[/title]: same call across multiple blocks
    - This is indicated by either the `--blocks` or `--time` parameters
    - Example: `call <addr1> <function-name> --time 30d`

## Multi-contract Calls

Example use case: Get a wallet's balances for many ERC20 tokens

Can use `--block` to select a specific block for calls

By default will use the first address's function abi for all calls
    [comment](Retrieve separate ABI's for each contract using `--unique-abis`)[/comment]

## Historical Calls

Example use case: Get the total supply of an ERC20 over time

Can specify historical calls by blocks or by timestamps

Ranges are inclusive of start and end boundaries

### Specifying historical calls using blocks

Example block specifications:
    `--blocks 16000 16010 16020 16030`
    `--blocks 16000,16010,16020,16030`
    `--blocks 16000, 16010, 16020, 16030`
    `--blocks 16010:16030:10`
    `--blocks 16010:16030 -n 4`
    (each of these examples specifies the same set of 4 blocks)

Can also specify a block range sampled over a regular time interval:
    `--blocks 15000000:16000000:1d` --> samples block range once per day

For block ranges with no interval specified, **all** blocks are used

### Specifying historical calls using timestamps

Example time specifications:
    `--times 20220701:20220730 -n 30`
    `--times 20220701:20220730:1d`
    `--times 20220701:29d -n 30`
    `--times 29d:20220701 -n 30`
    [comment](each of these examples specifies the same set of 30 timestamps)[/comment]

Can also use the current time as an implicit default:
    `--times 100d::1d`
    `--times 100d -n 101`
    `--times 100d: -n 101`
    `--times 100d:: -n 101`
    [comment](each of these examples specifies the same set of 100 timestamps)[/comment]

Can indicate timestamps using a variety of formats:

[timestamp table]

See the `tooltime` package for more information about time specifications

A default of `-n 25` is used if no `-n` is specified for time range

## Outputs

A table of outputs is displayed by default, omit with `--no-table`

Numerical outputs of historical calls are charted, omit with `--no-chart`

Use `--output` to output data to a json or csv file
More data is included when exporting to a file
"""


def get_command_help(parse_spec: toolcli.ParseSpec) -> str:
    styles = cli_run.get_cli_styles()
    stylized = stylize_markdown(command_help, styles=styles)
    stylized = stylized.replace(
        '[timestamp table]', get_timestamp_format_table()
    )
    stylized = stylized.replace('[comment]', '[' + styles['comment'] + ']')
    stylized = stylized.replace('[/comment]', '[/' + styles['comment'] + ']')
    return stylized


def get_timestamp_format_table() -> str:

    rows = [
        [
            'number + letter\n[comment](one of {yMdhms})[/comment]',
            'timelength',
            '100d\n24h',
        ],
        ['YYYY', 'start of year', '2018\n2022'],
        ['YYYYMM\nYYYY-MM', 'start of month', '201802\n2022-06'],
        ['YYYYMMDD\nYYYY-MM-DD', 'start of day', '20180228\n2022-06-01'],
        [
            'YYYYMMDD_HHMMSS\nYYYY-MM-DD_HH:MM',
            'minute in day',
            '20180228\n2022-06-01_04:30',
        ],
        [
            'YYYYMMDD_HHMMSS\nYYYY-MM-DD_HH:MM:SS',
            'second in day',
            '20180228\n2022-06-01_04:30:40',
        ],
        ['large number', 'unix timestamp', '1600000000\n1700000000'],
    ]

    labels = [
        'timestamp formats',
        'meaning',
        'examples',
    ]

    styles = cli_run.get_cli_styles()

    as_str = toolstr.print_multiline_table(
        rows,
        labels=labels,
        return_str=True,
        label_style=styles['title'],
        border=styles['comment'],
        column_styles={
            'timestamp formats': styles['option'],
            'meaning': styles['description'],
            'examples': styles['option'],
        },
        indent=4,
    )

    if not isinstance(as_str, str):
        raise Exception('did not return str')

    return as_str


def stylize_markdown(text: str, styles: toolcli.StyleTheme) -> str:

    import re

    lines = text.split('\n')

    code_regex = re.compile('`.*?`')
    bold_regex = re.compile('\*\*.*?\*\*')

    styled_lines = []
    for i, line in enumerate(lines):

        # stylize titles
        if line.startswith('#'):
            line = toolstr.add_style(line, styles['title'])

        if line.startswith('    - '):
            line = toolstr.add_style(line[:6], styles['title']) + line[6:]

        # replace code snippets
        for match in code_regex.findall(line):
            styled_match = toolstr.add_style(match.strip('`'), styles['option'])
            line = line.replace(match, styled_match)

        for match in bold_regex.findall(line):
            styled_match = toolstr.add_style(match.strip('*'), 'bold')
            line = line.replace(match, styled_match)

        styled_lines.append(line)

    return '\n'.join(styled_lines)


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_calls_command,
        'help': get_command_help,
        'args': [
            {
                'name': 'address_and_or_function',
                'nargs': '*',
                'help': '<see above>',
            },
            #
            # historical queries
            {
                'name': ['-b', '--blocks'],
                'nargs': '+',
                'help': 'block list or block range (see above)',
            },
            {
                'name': ['-t', '--times'],
                'nargs': '+',
                'help': 'timestamp list or time range (see above)',
            },
            {
                'name': '-n',
                'help': 'number of calls to make in given range',
                'type': int,
            },
            #
            # multi-address queries
            {
                'name': ['-a', '--addresses'],
                'nargs': '+',
                'help': 'addresses to point calls toward',
            },
            {'name': '--block', 'help': 'block number for calls'},
            {
                'name': '--unique-abis',
                'help': 'retrieve separate ABI for each address',
            },
            #
            # output parameters
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
                'name': '--no-table',
                'action': 'store_true',
                'help': 'do not output a table',
            },
            {
                'name': '--no-chart',
                'action': 'store_true',
                'help': 'do not output a chart',
            },
            #
            # advanced parameters
            {
                'name': '--from',
                'help': 'address that calls should come from',
                'dest': 'from_address',
            },
            {
                'name': '--normalize',
                'help': 'normalize output by value, default is 1) erc20 decimals or 2) "1e18"',
                'nargs': '*',
            },
            {
                'name': '--blocks-gte-times',
                'help': 'find the blocks >= timestamps instead of <=',
                'action': 'store_true',
            },
        ],
        'examples': {
            '<function_name> [<function_parameters>] --addresses <addresses>': {
                'description': '1) multi-contract template: same call across multiple addresses',
                'runnable': False,
            },
            '<address> <function_name> [<function_parameters>] --blocks <blocks>': {
                'description': '2) historical template: same call across multiple blocks',
                'runnable': False,
            },
            'balanceOf 0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7 --addresses 0x6b175474e89094c44da98b954eedeac495271d0f 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 0xdac17f958d2ee523a2206206994597c13d831ec7 --normalize': {
                'description': 'Balance of DAI, USDC, and USDT in Curve 3pool',
                'runnable': True,
            },
        },
    }


async def async_calls_command(
    *,
    address_and_or_function: typing.Sequence[str],
    blocks: typing.Sequence[str] | None,
    times: typing.Sequence[str] | None,
    n: int | None,
    addresses: typing.Sequence[str] | None,
    unique_abis: bool,
    block: str,
    output: str,
    overwrite: bool,
    no_table: bool,
    no_chart: bool,
    from_address: spec.Address | None,
    normalize: typing.Sequence[str],
    blocks_gte_times: bool,
) -> None:

    # check whether using multi contract query or historical query
    multi_contract_query = addresses is not None
    historical_query = blocks is not None or times is not None
    if multi_contract_query and historical_query:
        raise Exception('cannot specify --addresses and --blocks or --times')

    # resolve from address
    if from_address is not None:
        from_address = await evm.async_resolve_address(
            from_address, block=block
        )

    if multi_contract_query:

        if addresses is not None:
            addresses = await evm.async_resolve_addresses(
                addresses, block=block
            )
        if addresses is None:
            raise Exception('could not detect addresses')

        # multi-contract queries
        if block is None:
            block = 'latest'

        function_name, *function_parameters = address_and_or_function

        # assert that all address functions have the same number of outputs
        function_abi = await evm.async_get_function_abi(
            contract_address=addresses[0],
            function_name=function_name,
        )
        n_outputs = len(function_abi['outputs'])
        for to_address in addresses[1:]:
            other_function_abi = await evm.async_get_function_abi(
                contract_address=to_address,
                function_name=function_name,
            )
            if len(other_function_abi['outputs']) != n_outputs:
                print('toaddresses do not all have same number of function outputs')

        # fetch data
        if unique_abis:
            import asyncio

            coroutines = [
                rpc.async_batch_eth_call(
                    to_address=address,
                    function_name=function_name,
                    function_parameters=function_parameters,
                    block_number=block,
                    from_address=from_address,
                )
                for address in addresses
            ]
            results = await asyncio.gather(*coroutines)
        else:
            results = await rpc.async_batch_eth_call(
                to_addresses=addresses,
                function_name=function_name,
                function_parameters=function_parameters,
                block_number=block,
                from_address=from_address,
            )

        # name based on first contract's abi
        output_names = binary.get_function_output_names(
            function_abi, human_readable=True
        )

        if normalize is not None:
            if len(normalize) == 0:
                if len(output_names) != 1:
                    raise Exception(
                        'can only normalize functions that have a single output'
                    )
                try:
                    results = await evm.async_normalize_erc20s_quantities(
                        quantities=results,
                        tokens=addresses,
                    )
                except Exception:
                    result = [result / 1e18 for result in results]
            elif len(normalize) == 1:
                factor = float(normalize[0])
                results = [subresult / factor for subresult in results]
            else:
                raise Exception('--normalize should have at most 1 argument')

        styles = cli.get_cli_styles()
        toolstr.print_text_box('Multi-contract calls', style=styles['title'])
        if block is None:
            block = 'latest'
        cli.print_bullet(key='block', value=block)
        cli.print_bullet(key='function', value=function_name)
        cli.print_bullet(key='function_args', value='')
        for fp, function_parameter in enumerate(function_parameters):
            cli.print_bullet(value=function_parameter, number=fp + 1, indent=4)
        print()

        if output == 'stdout':
            rows = []
            for r, result in enumerate(results):
                row: list[typing.Any] = [addresses[0]]
                if len(output_names) == 1:
                    if normalize is not None:
                        row.append(result)
                    else:
                        row.append(str(result))
                else:
                    for subresult in result:
                        row.append(str(subresult))
                rows.append(row)
            labels: list[typing.Any] = ['address']
            for output_name in output_names:
                labels.append(output_name)
            toolstr.print_table(
                rows,
                labels=labels,
                border=styles['comment'],
                label_style=styles['title'],
                column_styles=[styles['metavar']]
                + [styles['description']] * len(output_names),
                column_formats={
                    'balanceOf': {'trailing_zeros': True, 'decimals': 2},
                },
            )
            return

        else:
            import pandas as pd

            df = pd.DataFrame(results, index=addresses)
            df.index.name = 'to_address'
            df.columns = output_names

    elif historical_query:

        # historical queries
        if block is not None:
            raise Exception(
                'cannot specify both --block alongside --blocks or --times'
            )

        # parse address, function, and function parameters
        (
            to_address,
            function_name,
            *function_parameters,
        ) = address_and_or_function
        to_address = await evm.async_resolve_address(to_address, block=block)

        # parse blocks or times
        if blocks is not None:

            # parse blocks
            block_numbers = await cli_utils.async_resolve_block_range(blocks)

        elif times is not None:

            # parse timestamps
            import tooltime

            if len(times) != 1:
                raise Exception('--times specified improperly')

            raw_timestamps = tooltime.parse_timeslice(times[0], n=n)
            timestamps = [int(timestamp) for timestamp in raw_timestamps]
            if blocks_gte_times:
                mode = '>='
            else:
                mode = '<='
            block_numbers = await evm.async_get_blocks_of_timestamps(
                timestamps,
                mode=mode,
                # mode='>=',
            )

        else:
            raise Exception('must specify --blocks or --times')

        # fetch data
        results = await rpc.async_batch_eth_call(
            to_address=to_address,
            function_name=function_name,
            function_parameters=function_parameters,
            block_numbers=block_numbers,
            from_address=from_address,
        )

        # get output names
        function_abi = await evm.async_get_function_abi(
            contract_address=to_address,
            function_name=function_name,
        )
        output_names = binary.get_function_output_names(
            function_abi, human_readable=True
        )

        styles = cli.get_cli_styles()
        toolstr.print_text_box('Historical calls', style=styles['title'])
        cli.print_bullet(key='address', value=toolstr.add_style(to_address, styles['metavar']))
        cli.print_bullet(key='function', value=function_name)
        cli.print_bullet(key='function_args', value='')
        for fp, function_parameter in enumerate(function_parameters):
            cli.print_bullet(value=function_parameter, number=fp + 1, indent=4)
        cli.print_bullet(key='# blocks', value=str(len(block_numbers)))
        print()

        if output == 'stdout':

            rows = []
            for r, result in enumerate(results):
                row = []
                row.append(blocks[r])
                if len(output_names) == 1:
                    row.append(result)
                else:
                    for subresult in result:
                        row.append(subresult)

                rows.append(row)
            labels = [
                'block',
            ]
            labels += output_names
            toolstr.print_table(rows, labels=labels)
            return

        else:

            # format into dataframe
            df = pd.DataFrame(results, index=block_numbers)
            df.index.name = 'block'
            df.columns = output_names

    else:
        raise Exception('must specify either --blocks or --addresses')

    cli_utils.output_data(data=df, output=output, overwrite=overwrite)
