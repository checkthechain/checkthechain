from __future__ import annotations

import math
import typing

import toolcli
import toolstr

from ctc import cli


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

    styles = cli.get_cli_styles()

    toolstr.print_text_box('int Limits', style=styles['title'])
    rows: typing.List[typing.Sequence[typing.Any]] = []
    for bit_value in bit_values:
        int_min = -(1 << (bit_value - 1))
        int_max = (1 << (bit_value - 1)) - 1
        row = [
            'int' + str(bit_value),
            str(int_min) + '\n ' + str(int_max),
        ]
        row[1] += (
            '\n-10^'
            + toolstr.format(round(math.log10(-int_min)))
            + ' --> 10^'
            + toolstr.format(round(math.log10(int_max)))
        )
        rows.append(row)
    toolstr.print_multiline_table(
        rows,
        column_justify=['right', 'left'],
        column_styles=[
            styles['option'] + ' bold',
            styles['description'],
        ],
        compact=1,
        separate_all_rows=False,
        vertical_justify='top',
    )

    # uint
    print()
    toolstr.print_text_box('uint Limits', style=styles['title'])
    rows = []
    for bit_value in bit_values:
        uint_max = 1 << bit_value
        row = ['uint' + str(bit_value), str(uint_max)]
        row[1] += '\n0 --> 10^' + str(round(math.log10(uint_max)))
        rows.append(row)
    toolstr.print_multiline_table(
        rows,
        column_justify=['right', 'left'],
        column_styles=[
            styles['option'] + ' bold',
            styles['description'],
        ],
        compact=1,
        separate_all_rows=False,
    )

    print()
    floats = [
        ['float16', 1, 5, 10, 3.31, '65500'],
        ['float32', 1, 8, 23, 7.22, '3.40e+38'],
        ['float64', 1, 11, 52, 15.95, '1.80e+308'],
        ['float128', 1, 15, 113, 34.32, '1.19e+4932'],
    ]
    labels = [
        'type',
        'sign\nbits',
        'exp\nbits',
        'mantissa\nbits',
        'decimal\ndigits',
        'max value',
    ]
    column_styles = {label: styles['description'] for label in labels}
    column_styles['type'] = styles['option'] + ' bold'
    toolstr.print_text_box('float Limits', style=styles['title'])
    toolstr.print_table(
        floats,
        labels=labels,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles=column_styles,  # type: ignore
    )

    print()
    print()
    toolstr.print_text_box('EVM Data', style=styles['title'])

    parameters = [
        ['address', '20 bytes'],
        ['transaction hash', '32 bytes'],
        ['word size', '32 bytes'],
        ['instruction size', '1 byte'],
    ]
    print()
    toolstr.print_table(
        rows=parameters,
        border=styles['comment'],
        column_styles=[styles['metavar'], styles['description']],
    )
    print()
    print()

    rows = [
        ['contract size', '0 bytes', '24576 bytes'],
        ['transaction size', '21000 gas', '30M gas'],
        ['block size', '0 gas', '30M gas'],
    ]
    toolstr.print_table(
        rows,
        labels=['', 'min', 'max'],
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            '': styles['metavar'],
            'min': styles['description'],
            'max': styles['description'],
        },
    )

    print()
    toolstr.print(
        'see '
        + toolstr.add_style('ctc gas -v', styles['option'] + ' bold')
        + ' for EVM gas cost summary',
        style=styles['comment'],
    )
