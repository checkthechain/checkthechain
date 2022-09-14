"""
TODO:
- add grouping for specific groups:
        - erc20 functions and events
        - proxy functions
        - erc721 erc1155
    - could group these either spatially or by color
- add listing of unknown signatures
- add event signatures
"""
from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import rpc


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_decompile_command,
        'help': 'decompile contract abi',
        'args': [
            {
                'name': 'address_or_bytecode',
                'help': 'contract address or hex bytecode',
            },
            {
                'name': ['-v', '--verbose'],
                'help': 'do not clip long names',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        ],
    }


async def async_decompile_command(
    address_or_bytecode: str, verbose: bool
) -> None:

    address_or_bytecode = await evm.async_resolve_address(address_or_bytecode)

    if len(address_or_bytecode) == 42:
        bytecode = await rpc.async_eth_get_code(address_or_bytecode)
    else:
        bytecode = address_or_bytecode

    # get function selectors
    function_selectors = evm.extract_bytecode_function_selectors(bytecode)
    function_selector_indices = {
        function_selector: index
        for index, function_selector in enumerate(sorted(function_selectors))
    }

    # match against 4bytes
    decompiled_function_abis = await evm.async_decompile_function_abis(
        bytecode,
        sort='hex_signature',
    )

    styles = cli.get_cli_styles()
    toolstr.print(
        'Found '
        + toolstr.add_style(
            str(len(function_selectors)),
            styles['description'] + ' bold',
        )
        + ' function selectors matching '
        + toolstr.add_style(
            str(len(decompiled_function_abis)),
            styles['description'] + ' bold',
        )
        + ' total 4byte entries',
    )

    if len(decompiled_function_abis) > 0:
        print()
        toolstr.print_header('Known selectors', style=styles['title'])
    rows: typing.MutableSequence[typing.MutableSequence[typing.Any]] = []
    row = None
    for e, entry in enumerate(decompiled_function_abis):

        duplicate = (
            e > 0
            and entry['hex_signature']
            == decompiled_function_abis[e - 1]['hex_signature']
        )

        if duplicate and row is not None:
            row[2] = row[2] + '\n' + entry['text_signature']
            # row = [
            #     '',
            #     '',
            #     entry['text_signature'],
            # ]
        else:
            if row is not None:
                rows.append(row)
            row = [
                function_selector_indices[entry['hex_signature']],
                entry['hex_signature'],
                entry['text_signature'],
            ]
    if verbose:
        width = None
    else:
        width = toolcli.get_n_terminal_cols()

    print()
    toolstr.print_multiline_table(
        rows,
        column_justify=['right', 'right', 'left'],
        # add_row_index=True,
        labels=['', 'selector', '4byte matches'],
        border=styles['comment'],
        label_style=styles['title'],
        column_styles=[
            styles['title'] + ' bold',
            styles['metavar'],
            styles['description'],
        ],
        # compact=2,
        max_table_width=width,
        # indent=4,
    )

    decompiled_selectors = set(
        entry['hex_signature'] for entry in decompiled_function_abis
    )
    unknown_selectors = set(function_selectors) - decompiled_selectors
    if len(unknown_selectors) > 0:
        print()
        toolstr.print_header('Unknown selectors', style=styles['title'])
        for unknown_selector in unknown_selectors:
            print(unknown_selector)

    if len(decompiled_function_abis) == 0:
        print()
        print('could not detect any function signatures')
