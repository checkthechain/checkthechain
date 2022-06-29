from __future__ import annotations

import typing

import toolcli
import toolstr


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': limits_command,
        'help': 'display limits of various datatypes',
        'args': [
            {
                'name': ['--verbose', '-v'],
                'help': 'display all possible bit values',
                'action': 'store_true',
            },
            {
                'name': ['--bits', '-b'],
                'help': 'specify number of bits, either single or as list',
                'nargs': '+',
            },
        ],
        'examples': [
            '',
            '--verbose',
            '--bits 256 512 1024',
        ],
    }


def limits_command(verbose: bool, bits: list[str]) -> None:
    if bits is not None:
        bit_tokens = bits
        bit_tokens = [
            value for token in bit_tokens for value in token.split(',')
        ]
        bit_tokens = [
            value for token in bit_tokens for value in token.split(' ')
        ]
        bit_values = [int(token) for token in bit_tokens]
    elif verbose:
        bit_values = list(range(8, 256 + 8, 8))
    else:
        bit_values = [
            8,
            16,
            32,
            64,
            128,
            192,
            256,
        ]

    toolstr.print_text_box('int')
    rows: typing.List[typing.Sequence[typing.Any]] = [
        [
            'int' + str(bit_value),
            'min\nmax',
            str(-(1 << (bit_value - 1)))
            + '\n '
            + str((1 << (bit_value - 1)) - 1),
        ]
        for bit_value in bit_values
    ]
    toolstr.print_multiline_table(
        rows,
        column_justify=['right', 'right', 'left'],
        compact=2,
        separate_all_rows=False,
    )

    # uint
    print()
    toolstr.print_text_box('uint')
    rows = [
        ['uint' + str(bit_value), 'max', str(1 << bit_value)]
        for bit_value in bit_values
    ]
    toolstr.print_table(rows, column_justify=['right', 'center', 'left'], compact=2)
