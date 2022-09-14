from __future__ import annotations

import asyncio
import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_call_all_command,
        'help': 'display outputs of all contract\'s read-only functions'
        + '\n\ncurrently only displays output of zero-parameter functions',
        'args': [
            {
                'name': 'contract_address',
                'help': 'address of contract to call functions of',
            },
            {
                'name': '--max-results',
                'default': 10,
                'type': int,
                'help': 'for functions that output lists, limit display length',
            },
            {
                'name': '--block',
                'help': 'block number for call',
            },
        ],
        'examples': [
            '0x6c3f90f043a72fa612cbac8115ee7e52bde6e490',
            '0x240315db938d44bb124ae619f5fd0269a02d1271 --max-results 5',
        ],
    }


async def async_call_all_command(
    *,
    contract_address: spec.Address,
    max_results: int,
    block: str,
) -> None:

    if block is not None:
        block_number = await evm.async_block_number_to_int(block)
    else:
        block_number = 'latest'

    contract_abi = await evm.async_get_contract_abi(contract_address)

    function_abis = []
    coroutines = []
    for item in contract_abi:
        if item.get('type') == 'function':
            if typing.TYPE_CHECKING:
                function_abi = typing.cast(spec.FunctionABI, item)
            else:
                function_abi = item
            if evm.is_function_read_only(function_abi):
                inputs = function_abi.get('inputs')
                if inputs is not None and len(inputs) == 0:
                    function_abis.append(function_abi)
                    coroutine = rpc.async_eth_call(
                        to_address=contract_address,
                        function_abi=function_abi,
                        provider={'convert_reverts_to_none': True},
                        block_number=block_number,
                    )
                    coroutines.append(coroutine)

    results = await asyncio.gather(*coroutines)

    styles = cli.get_cli_styles()

    multiline = False
    rows = []
    for r in range(len(results)):
        function_abi = function_abis[r]
        row = [function_abi['name']]
        result = results[r]

        # modify specific result values
        if result is None:
            result = toolstr.add_style('\[REVERT]', styles['title'])
        if isinstance(result, int):
            result = str(result)

        # add result to row
        if isinstance(result, (tuple, list)):
            import json

            footnote = 'length = ' + str(len(result))
            if len(result) > max_results:
                footnote += ', clipped to ' + str(max_results)
                result = result[:max_results]
                clipped = True
            else:
                clipped = False
            str_result = json.dumps(result, sort_keys=True, indent=2)
            if clipped:
                str_result = str_result[: str_result.rindex('\n')]
                str_result = str_result + ',\n...'

            footnote = toolstr.add_style(
                '(' + footnote + ')', styles['comment']
            )
            str_result += '\n\n' + footnote
            row.append(str_result)
            multiline = True
        else:
            row.append(result)

        rows.append(row)

    labels = [
        'function',
        'output',
    ]

    toolstr.print_text_box(
        'Function Outputs for ' + contract_address, style=styles['title']
    )
    print()
    if multiline:
        toolstr.print_multiline_table(
            rows,
            labels=labels,
            indent=4,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'function': styles['option'],
                'output': styles['description'],
            },
            column_justify={'output': 'raw'},
        )
    else:
        toolstr.print_table(
            rows,
            labels=labels,
            indent=4,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'function': styles['option'],
                'output': styles['description'],
            },
        )
