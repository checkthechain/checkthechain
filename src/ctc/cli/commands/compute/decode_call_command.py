from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import binary
from ctc import evm
from ctc.cli import cli_run


help_message = """decode EVM call data

syntax is one of
    1. [option]ctc CALL_DATA[/option]
    2. [option]ctc CONTRACT_ADDRESS CALL_DATA[/option]"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_decode_command,
        'help': help_message,
        'args': [
            {
                'name': 'args',
                'help': 'either `CALL_DATA` or `CONTRACT_ADDRESS CALL_DATA`',
                'nargs': '+',
            },
            {
                'name': '--nested',
                'help': 'whether to decode nested calls',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0xdac17f958d2ee523a2206206994597c13d831ec7 0xa9059cbb00000000000000000000000021dd5c13925407e5bcec3f27ab11a355a9dafbe3000000000000000000000000000000000000000000000000000000003fd629c0',
            '0xeefba1e63905ef1d7acba5a8513c70307c1ce441 0x252dba420000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000100000000000000000000000000a65803ad604668e26a81be92c9f1c90354255eae00000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000044bba06f270000000000000000000000000a01960ddf19c59e43cbdf0b5ab9278d7459e76e000000000000000000000000e9822f18f2654e606a8dff9d75edd98367e7c0ae00000000000000000000000000000000000000000000000000000000000000000000000000000000a65803ad604668e26a81be92c9f1c90354255eae0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000002451cff8d90000000000000000000000000a01960ddf19c59e43cbdf0b5ab9278d7459e76e00000000000000000000000000000000000000000000000000000000 --nested',
        ],
    }


async def async_decode_command(
    *,
    args: typing.Sequence[str],
    nested: bool,
    title: str | None = None,
    indent: str | None = None,
    mention_nested: bool = True,
) -> None:

    styles = cli_run.get_cli_styles()

    if len(args) == 1:
        from ctc.protocols import fourbyte_utils

        call_data = args[0]
        signature = call_data[:10]
        result = await fourbyte_utils.async_query_function_signatures(signature)
        print(result)
        return
    elif len(args) == 2:
        contract_address, call_data = args
        contract_abi = await evm.async_get_contract_abi(
            contract_address=contract_address
        )
        decoded = binary.decode_call_data(
            contract_abi=contract_abi, call_data=call_data
        )
        function_abi = decoded['function_abi']
    else:
        raise Exception('wrong syntax, see `ctc decode -h`')

    def print_bullet(
        key: typing.Any,
        value: typing.Any = '',
        indent: str = '',
        bullet: str = '-',
        key_style: str | None = None,
    ) -> None:
        if key_style is None:
            key_style = styles['option']
        toolstr.print(
            indent
            + toolstr.add_style(bullet + ' ', styles['title'])
            + toolstr.add_style(str(key), key_style)
            + toolstr.add_style(': ', styles['comment'])
            + toolstr.add_style(str(value), styles['description'] + ' bold')
        )

    # print header
    if indent is None:
        indent = ''
    if title is None:
        title = 'Decoding Call Data'
    toolstr.print_text_box(title, style=styles['title'])
    print_bullet('to', contract_address, indent)
    print_bullet('n_bytes', len(binary.convert(call_data, 'binary')), indent)
    print()

    # print funciton info
    print()
    toolstr.print_header('Function Info', style=styles['title'])
    print_bullet('name', function_abi['name'], indent)
    print_bullet('selector', decoded['function_selector'], indent)
    print_bullet(
        'signature', binary.get_function_signature(function_abi), indent
    )
    print_bullet('inputs', indent=indent)
    for p, parameter in enumerate(function_abi['inputs']):
        print_bullet(
            parameter['name'],
            parameter['type'],
            indent=indent + '    ',
            bullet=str(p + 1) + '.',
        )
    print_bullet('outputs', indent=indent)
    for p, parameter in enumerate(function_abi['outputs']):
        print_bullet(
            parameter['name'],
            parameter['type'],
            indent=indent + '    ',
            bullet=str(p + 1) + '.',
        )
    if len(function_abi['outputs']) == 0:
        toolstr.print(indent + '    \[no outputs]', style=styles['comment'])
    print()

    # print function parameters
    if nested:
        if len(function_abi['inputs']) != 1:
            raise NotImplementedError(
                'only implemented for simple lists of calls'
            )
        nested_calls = decoded['parameters'][0]
        for nc, nested_call in enumerate(nested_calls):
            nested_address, nested_call_data = nested_call
            title = (
                'Nested Call Data '
                + str(nc + 1)
                + ' / '
                + str(len(nested_calls))
            )
            print()
            await async_decode_command(
                args=nested_call,
                nested=False,
                title=title,
                indent='',
                mention_nested=False,
            )
            if nc + 1 != len(nested_calls):
                print()

    else:
        print()
        toolstr.print_header('Call Parameters', style=styles['title'])
        input_names = binary.get_function_parameter_names(function_abi)
        for p, parameter in enumerate(decoded['parameters']):
            if isinstance(parameter, tuple):
                print_bullet(
                    str(input_names[p]),
                    indent=indent,
                    bullet=str(p + 1) + '.',
                )
                for subparameter in parameter:
                    toolstr.print(
                        indent + '    ' + stringify(subparameter),
                        style=styles['description'],
                    )
                if len(parameter) == 0:
                    toolstr.print(
                        indent + '    \[none]', style=styles['comment']
                    )
            else:
                print_bullet(
                    input_names[p],
                    parameter,
                    indent=indent,
                    bullet=str(p + 1) + '.',
                )

    if mention_nested and not nested:
        toolstr.print(
            'use --nested to decode nested calls',
            style=styles['comment'],
        )


def stringify(item: typing.Any) -> str:
    return str(item)
    if isinstance(item, tuple):
        return str(list(stringify(subitem) for subitem in item))
    else:
        return str(item)
