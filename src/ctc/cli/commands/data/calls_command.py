"""
TODO:
- allow using function selector instead of function name
- allow using quoted json to indicate function abi
- --normalize arg to normalize outputs
- be able to use ERC20 symbols in addresses
"""

from __future__ import annotations

import asyncio
import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.cli import cli_utils


command_help = """output the result of multiple contract eth_call's

This command can be used in two ways:

[title]1) [option]**Multi-contract Calls**[/option][/title][comment]:[/comment] same call across multiple contracts
    - This is indicated by the `--addresses` parameter
    - Example: `call <function> --addresses <addr1> <addr2> <addr3>`

[title]2) [option]**Multi-block Calls**[/option][/title][comment]:[/comment] same call across multiple blocks
    - This is indicated by either of the `--blocks` or `--time` parameters
    - Example: `call <addr1> <function> --time 30d`

[comment]in each case, `<function>` can be a name, a 4byte selector, or an ABI[/comment]

## Multi-contract Calls

Example use case: Get a wallet's balances for many ERC20 tokens

Can use `--block` to select a specific block for calls

By default will use the first address's function abi for all calls
    [comment](Retrieve separate ABI's for each contract using `--unique-abis`)[/comment]

## Multi-block Calls

Example use case: Get the total supply of an ERC20 over time

Can specify multi-block calls by blocks or by timestamps

Ranges are inclusive of start and end boundaries

### Specifying multi-block calls using `--blocks`

Example block specifications:
    `--blocks 16000 16010 16020 16030`
    `--blocks 16010:16030:10`
    `--blocks 16010:16030 -n 4`
    `--blocks 16030:-20:10`
    `--blocks latest:-20:10`
    [comment](each of these examples would specify the same set of 4 blocks,
     if the latest block were 16030)[/comment]

Can also specify a block range sampled over a regular time interval:
    `--blocks 15000000:16000000:1d` --> samples block range once per day

For block ranges with no interval specified, **all** blocks are used

### Specifying multi-block calls using `--times`

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

Numerical outputs of multi-block calls are charted, omit with `--no-chart`

Use `--export` to output data to a json or csv file
More data is included when exporting to a file
"""


def get_command_help(parse_spec: toolcli.ParseSpec) -> str:
    styles = cli.get_cli_styles()
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

    styles = cli.get_cli_styles()

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
            # multi-block queries
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
                'name': '--export',
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
            '<function> [<function_parameters>] --addresses <addresses>': {
                'description': '1) multi-contract template: same call across multiple addresses',
                'runnable': False,
            },
            '<address> <function> [<function_parameters>] --blocks <blocks>': {
                'description': '2) multi-block template: same call across multiple blocks',
                'runnable': False,
            },
            'balanceOf 0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7 --addresses 0x6b175474e89094c44da98b954eedeac495271d0f 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 0xdac17f958d2ee523a2206206994597c13d831ec7 --normalize': {
                'description': 'Balance of DAI, USDC, and USDT in Curve 3pool',
                'runnable': True,
            },
            '0x6b175474e89094c44da98b954eedeac495271d0f balanceOf 0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7 --times 2021:2022:1w --normalize': {
                'description': 'Weekly balance of DAI in Curve 3pool throughout year 2021',
                'runnable': True,
            },
            '0x6b175474e89094c44da98b954eedeac495271d0f balanceOf 0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7 --blocks latest:-1000000 -n 20 --normalize': {
                'description': 'Balance of DAI in Curve 3pool over the past 1 million blocks',
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
    export: str,
    overwrite: bool,
    no_table: bool,
    no_chart: bool,
    from_address: spec.Address | None,
    normalize: typing.Sequence[str],
    blocks_gte_times: bool,
) -> None:

    # check whether using multi-contract query or multi-block query
    multi_contract_query = addresses is not None
    multi_block_query = blocks is not None or times is not None
    if multi_contract_query and multi_block_query:
        raise Exception('cannot specify --addresses and --blocks or --times')

    # resolve from address
    if from_address is not None:
        from_address = await evm.async_resolve_address(
            from_address, block=block
        )

    if multi_contract_query:
        df: spec.DataFrame | None = await async_perform_multi_contract_call(
            address_and_or_function=address_and_or_function,
            addresses=addresses,
            block=block,
            unique_abis=unique_abis,
            from_address=from_address,
            normalize=normalize,
            export=export,
        )

    elif multi_block_query:
        df = await async_perform_multi_block_call(
            address_and_or_function=address_and_or_function,
            blocks=blocks,
            times=times,
            n=n,
            addresses=addresses,
            block=block,
            export=export,
            no_table=no_table,
            no_chart=no_chart,
            from_address=from_address,
            normalize=normalize,
            blocks_gte_times=blocks_gte_times,
        )

    else:
        raise Exception('must specify either --blocks or --addresses')

    if export != 'stdout':
        if df is None:
            raise Exception('did not obtain dataframe of data')
        cli_utils.output_data(data=df, output=export, overwrite=overwrite)


async def async_perform_multi_contract_call(
    *,
    address_and_or_function: typing.Sequence[str],
    addresses: typing.Sequence[spec.Address] | None,
    block: str,
    unique_abis: bool,
    from_address: spec.Address | None,
    normalize: typing.Sequence[str],
    export: str,
) -> spec.DataFrame | None:

    if addresses is not None:
        addresses = await evm.async_resolve_addresses(addresses, block=block)
    if addresses is None:
        raise Exception('could not detect addresses')

    # multi-contract queries
    if block is None:
        block = 'latest'

    function, *function_parameters = address_and_or_function

    # assert that all address functions have the same number of outputs
    function_abi = await evm.async_parse_function_str_abi(
        function,
        contract_address=addresses[0],
    )
    n_outputs = len(function_abi['outputs'])
    for to_address in addresses[1:]:
        other_function_abi = await evm.async_get_function_abi(
            contract_address=to_address,
            function_name=function_abi['name'],
        )
        if len(other_function_abi['inputs']) != len(function_abi['inputs']):
            print('not all addresses have same number of function inputs')
        if len(other_function_abi['outputs']) != n_outputs:
            print('not all addresses have same number of function outputs')

    # fetch data
    if unique_abis:
        import asyncio

        coroutines = [
            rpc.async_batch_eth_call(
                to_address=address,
                function_abi=function_abi,
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
            function_abi=function_abi,
            function_parameters=function_parameters,
            block_number=block,
            from_address=from_address,
        )

    # name based on first contract's abi
    output_names = evm.get_function_output_names(
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
                results = [result / 1e18 for result in results]
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
    cli.print_bullet(key='function', value=function_abi.get('name', '\[none]'))
    cli.print_bullet(key='function_args', value='')
    for fp, function_parameter in enumerate(function_parameters):
        cli.print_bullet(value=function_parameter, number=fp + 1, indent=4)
    print()

    if export == 'stdout':
        rows = []
        for r, result in enumerate(results):
            row: list[typing.Any] = [addresses[r]]
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
        return None

    else:
        import pandas as pd

        df = pd.DataFrame(results, index=addresses)
        df.index.name = 'to_address'
        df.columns = output_names

        return df


async def async_perform_multi_block_call(
    *,
    address_and_or_function: typing.Sequence[str],
    blocks: typing.Sequence[str] | None,
    times: typing.Sequence[str] | None,
    n: int | None,
    addresses: typing.Sequence[str] | None,
    block: str,
    export: str,
    no_table: bool,
    no_chart: bool,
    from_address: spec.Address | None,
    normalize: typing.Sequence[str],
    blocks_gte_times: bool,
) -> spec.DataFrame | None:

    # historical queries
    if block is not None:
        raise Exception(
            'cannot specify both --block alongside --blocks or --times'
        )
    if addresses is not None:
        raise Exception('cannot specify --addresses in multi block call')

    # parse address, function, and function parameters
    (
        to_address,
        function,
        *function_parameters,
    ) = address_and_or_function
    to_address = await evm.async_resolve_address(to_address, block=block)
    function_abi = await evm.async_parse_function_str_abi(
        function,
        contract_address=to_address,
    )

    # parse blocks or times
    if blocks is not None:

        # parse blocks
        block_numbers = await cli_utils.async_parse_block_slice(blocks, n=n)

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

    if not no_table:
        block_timestamps_coroutine = evm.async_get_block_timestamps(
            block_numbers
        )
        block_timestamps_task = asyncio.create_task(block_timestamps_coroutine)

    # fetch data
    results = await rpc.async_batch_eth_call(
        to_address=to_address,
        function_abi=function_abi,
        function_parameters=function_parameters,
        block_numbers=block_numbers,
        from_address=from_address,
    )

    output_names = evm.get_function_output_names(
        function_abi, human_readable=True
    )
    if normalize is not None:
        if len(normalize) == 0:
            if len(output_names) != 1:
                raise Exception(
                    'can only normalize functions that have a single output'
                )
            try:
                results = await evm.async_normalize_erc20_quantities(
                    quantities=results,
                    token=to_address,
                )
            except Exception:
                result = [result / 1e18 for result in results]
        elif len(normalize) == 1:
            factor = float(normalize[0])
            results = [subresult / factor for subresult in results]
        else:
            raise Exception('--normalize should have at most 1 argument')

    styles = cli.get_cli_styles()
    toolstr.print_text_box('Multi-block calls', style=styles['title'])
    cli.print_bullet(
        key='address', value=toolstr.add_style(to_address, styles['metavar'])
    )
    cli.print_bullet(key='function', value=function_abi.get('name', '\[none]'))
    cli.print_bullet(key='function_args', value='')
    for fp, function_parameter in enumerate(function_parameters):
        cli.print_bullet(value=function_parameter, number=fp + 1, indent=4)
    cli.print_bullet(key='# blocks', value=str(len(block_numbers)))
    print()

    if export == 'stdout':

        import tooltime

        if not no_table:

            block_timestamps = await block_timestamps_task

            rows = []
            for r, result in enumerate(results):
                row = []
                row.append(block_numbers[r])
                age = tooltime.get_age(block_timestamps[r], 'TimelengthPhrase')
                age = ', '.join(age.split(', ')[:2])
                row.append(age)
                if len(output_names) == 1:
                    row.append(result)
                else:
                    for subresult in result:
                        row.append(subresult)

                rows.append(row)
            labels = [
                'block',
                'block age',
            ]
            labels += output_names
            column_styles = {
                'block': styles['option'],
                'block age': styles['option'],
            }
            column_formats = {
                'block': {'commas': False},
            }
            for output_name in output_names:
                column_styles[output_name] = styles['description']
                if normalize is not None:
                    column_formats[output_name] = {'trailing_zeros': True}
            print()
            toolstr.print_table(
                rows,
                labels=labels,
                border=styles['comment'],
                label_style=styles['title'],
                column_styles=column_styles,
                column_formats=column_formats,
                indent=4,
            )

        if not no_chart:

            xvals = block_numbers
            yvals = results
            plot = toolstr.render_line_plot(
                xvals=xvals,
                yvals=yvals,
                n_rows=40,
                n_columns=120,
                line_style=styles['description'],
                chrome_style=styles['comment'],
                tick_label_style=styles['metavar'],
                xaxis_kwargs={'tick_label_format': None, 'n_ticks': 2},
            )
            print()
            print()
            toolstr.print(
                toolstr.hjustify(output_names[0], 'center', 70),
                indent=4,
                style=styles['title'],
            )
            toolstr.print(plot, indent=4)

        return None

    else:
        import pandas as pd

        # format into dataframe
        df = pd.DataFrame(results, index=block_numbers)
        df.index.name = 'block'
        df.columns = output_names
        return df
