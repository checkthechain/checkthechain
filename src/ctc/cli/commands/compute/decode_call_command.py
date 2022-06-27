from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import binary
from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_decode_command,
        'help': """decode EVM call data

syntax is one of
    [option]ctc CALL_DATA[/option]
    [option]ctc CONTRACT_ADDRESS CALL_DATA[/option]""",
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
        'examples': ['0x956f47f50a910163d8bf957cf5846d573e7f87ca'],
    }


async def async_decode_command(
    *,
    args: typing.Sequence[str],
    nested: bool,
    title: str | None = None,
    indent: str | None = None,
) -> None:
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

    # print header
    if indent is None:
        indent = ''
    if title is None:
        title = 'Decoding Call Data'
    toolstr.print_text_box(title)
    print(indent + '- n_bytes:', len(binary.convert(call_data, 'binary')))
    print()

    # print funciton info
    toolstr.print_header('Function Info')
    print(indent + '- name:', function_abi['name'])
    print(indent + '- selector:', decoded['function_selector'])
    print(indent + '- signature:', binary.get_function_signature(function_abi))
    print(indent + '- inputs:')
    for p, parameter in enumerate(function_abi['inputs']):
        print(
            indent + '    ',
            str(p + 1) + '.',
            parameter['name'],
            parameter['type'],
        )
    print(indent + '- outputs:')
    for p, parameter in enumerate(function_abi['outputs']):
        print(
            indent + '    ',
            str(p + 1) + '.',
            parameter['name'],
            parameter['type'],
        )
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
            )

    else:
        toolstr.print_header('Function Parameters')
        input_names = binary.get_function_parameter_names(function_abi)
        for p, parameter in enumerate(decoded['parameters']):
            if isinstance(parameter, tuple):
                print(indent + str(p + 1) + '.', str(input_names[p]) + ':')
                for subparameter in parameter:
                    print(indent + '    ' + str(subparameter))
            else:
                print(
                    indent + str(p + 1) + '.',
                    str(input_names[p]) + ':',
                    parameter,
                )
