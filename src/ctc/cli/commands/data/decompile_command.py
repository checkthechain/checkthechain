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

import os

import toolcli
import toolstr

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

    print(
        'Found',
        len(function_selectors),
        'function selectors matching',
        len(decompiled_function_abis),
        'total 4byte entries',
    )

    if len(decompiled_function_abis) > 0:
        print()
        toolstr.print_header('Known selectors')
    rows = []
    for entry in decompiled_function_abis:
        row = [
            function_selector_indices[entry['hex_signature']],
            entry['hex_signature'],
            entry['text_signature'],
        ]
        rows.append(row)
    if verbose:
        width = None
    else:
        try:
            width = os.get_terminal_size().columns
        except Exception:
            width = 80
    toolstr.print_table(
        rows,
        column_justify=['right', 'right', 'left'],
        # add_row_index=True,
        compact=2,
        max_table_width=width,
    )

    decompiled_selectors = set(
        entry['hex_signature'] for entry in decompiled_function_abis
    )
    unknown_selectors = set(function_selectors) - decompiled_selectors
    if len(unknown_selectors) > 0:
        print()
        toolstr.print_header('Unknown selectors')
        for unknown_selector in unknown_selectors:
            print(unknown_selector)

    if len(decompiled_function_abis) == 0:
        print()
        print('could not detect any function signatures')
