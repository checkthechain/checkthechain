from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import spec


help_message = """decode EVM call data

syntax is one of
    1. [option]ctc decode call CALL_DATA[/option]
    2. [option]ctc decode call CONTRACT_ADDRESS CALL_DATA[/option]
    3. [option]ctc decode call TX_HASH --tx[/option]"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_decode_call_command,
        'help': help_message,
        'args': [
            {
                'name': 'args',
                'help': '`CALL_DATA` or `CONTRACT_ADDRESS CALL_DATA` or `TX_HASH`',
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
            '0xeefba1e63905ef1d7acba5a8513c70307c1ce441 0x252dba420000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000100000000000000000000000000a65803ad604668e26a81be92c9f1c90354255eae00000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000044bba06f270000000000000000000000000a01960ddf19c59e43cbdf0b5ab9278d7459e76e000000000000000000000000e9822f18f2654e606a8dff9d75edd98367e7c0ae00000000000000000000000000000000000000000000000000000000000000000000000000000000a65803ad604668e26a81be92c9f1c90354255eae0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000002451cff8d90000000000000000000000000a01960ddf19c59e43cbdf0b5ab9278d7459e76e00000000000000000000000000000000000000000000000000000000',
            '0xcb2931bd1c078f70106017f2e0c378fa9f648aa7d17c1d87240764b65e4626c9',
        ],
    }


async def async_decode_call_command(
    *,
    args: typing.Sequence[str],
    nested: bool = False,
    title: str | None = None,
    indent: str | None = None,
    mention_nested: bool = True,
    send_value: int | None = None,
    explicit_signature: str | None = None,
) -> None:

    tx = len(args) == 1 and (
        (args[0].startswith('0x') and len(args[0]) == 66)
        or (len(args[0]) == 64)
    )

    styles = cli.get_cli_styles()
    # print header
    if indent is None:
        indent = ''
    if title is None:
        title = 'Decoding Call Data'
    toolstr.print_text_box(title, style=styles['title'])

    if tx:
        if len(args) != 1:
            raise Exception('syntax is `ctc decode call TX_HASH --tx`')
        transaction = await evm.async_get_transaction(args[0])
        call_data = transaction['input']
        contract_address = transaction['to']
        contract_known = True
    elif len(args) == 1:
        from ctc.protocols import fourbyte_utils

        contract_known = False
        call_data = args[0]
        signature = call_data[:10]
        result = await fourbyte_utils.async_query_function_signatures(signature)

        for subresult in result:
            try:
                function_abi: spec.FunctionABI | None = (
                    evm.function_signature_to_abi(subresult['text_signature'])
                )
                decoded = evm.decode_call_data(
                    call_data=call_data,
                    function_abi=function_abi,
                )
                break
            except Exception as e:
                raise e
                continue
        else:
            raise Exception(
                'could not identify suitable abi for decoding function'
            )

    elif len(args) == 2:
        contract_address, call_data = args
        contract_known = True
    else:
        raise Exception('wrong syntax, see `ctc decode -h`')

    if contract_known:
        try:
            contract_abi = await evm.async_get_contract_abi(
                contract_address=contract_address
            )
            if explicit_signature is not None:
                function_selector = evm.get_function_selector(
                    function_signature=explicit_signature
                )
                call_data = (
                    '0x'
                    + function_selector
                    + evm.binary_convert(call_data, 'raw_hex')
                )

            decoded = evm.decode_call_data(
                contract_abi=contract_abi, call_data=call_data
            )
            function_abi = decoded['function_abi']
        except Exception:
            function_abi = None

    def print_bullet(
        key: typing.Any,
        value: typing.Any = '',
        indent: str = '',
        bullet: str = '-',
        key_style: str | None = None,
    ) -> None:
        if key_style is None:
            key_style = styles['option']

        as_str = indent + toolstr.add_style(bullet + ' ', styles['title'])
        if key != '':
            as_str += toolstr.add_style(
                str(key), key_style
            ) + toolstr.add_style(': ', styles['comment'])
        as_str += toolstr.add_style(str(value), styles['description'] + ' bold')
        toolstr.print(as_str)

    if contract_known:
        print_bullet('to', contract_address, indent)
    print_bullet(
        'n_bytes', len(evm.binary_convert(call_data, 'binary')), indent
    )
    if send_value is not None:
        print_bullet('value', send_value, indent)

    if function_abi is None:
        if explicit_signature is not None:
            print_bullet('signature', explicit_signature)
        print()
        if contract_known:
            print(
                '[abi for ' + contract_address + ' unavailable, cannot decode]'
            )
        else:
            print('[abi unavailable, cannot decode]')
        return

    # print funciton info
    print()
    print()
    toolstr.print_header('Function Info', style=styles['title'])
    print_bullet('name', function_abi['name'], indent)
    print_bullet('selector', decoded['function_selector'], indent)
    if explicit_signature is not None:
        print_bullet('signature', explicit_signature)
    else:
        print_bullet(
            'signature', evm.get_function_signature(function_abi), indent
        )
    print_bullet('inputs', indent=indent)
    for p, parameter in enumerate(function_abi['inputs']):
        if 'name' in parameter:
            cli.print_bullet(
                key=parameter['name'],
                value=parameter['type'],
                indent=indent + '    ',
                number=p + 1,
            )
        else:
            cli.print_bullet(
                value=parameter['type'],
                colon_str='',
                indent=indent + '    ',
                number=p + 1,
            )
    print_bullet('outputs', indent=indent)
    for p, parameter in enumerate(function_abi['outputs']):
        if 'name' in parameter:
            cli.print_bullet(
                key=parameter['name'],
                value=parameter['type'],
                indent=indent + '    ',
                number=(p + 1),
            )
        else:
            cli.print_bullet(
                key=parameter['name'],
                value=parameter['type'],
                indent=indent + '    ',
                number=(p + 1),
            )
    if len(function_abi['outputs']) == 0:
        toolstr.print(indent + '    \[no outputs]', style=styles['comment'])
    print()

    # detect nested calls
    nested_calls = []
    non_nested_parameters = list(range(len(decoded['parameters'])))
    named_parameters = decoded.get('named_parameters')

    function_selector = evm.get_function_selector(function_abi)
    if not nested:
        nested = function_selector in [
            '252dba42',  # aggregate((address,bytes)[])
            '7d5e81e2',  # propose(address[],uint256[],bytes[],string)
            '40a4f325',  # executeBatch(address,address[],uint256[],bytes[],bytes32,bytes32)
        ]

    if nested:

        if len(function_abi['inputs']) == 1:
            nested_calls = [
                {
                    'address': address,
                    'call_data': call_data,
                    'value': None,
                    'signature': None,
                }
                for address, call_data in decoded['parameters'][0]
            ]
            non_nested_parameters = []
        elif (
            named_parameters is not None
            and 'targets' in named_parameters
            and 'calldatas' in named_parameters
        ):

            # gather nested calls
            nested_calls = []
            for i in range(len(named_parameters['calldatas'])):
                nested_call = {
                    'address': named_parameters['targets'][i],
                    'call_data': named_parameters['calldatas'][i],
                    'value': None,
                    'signature': None,
                }
                if 'values' in named_parameters:
                    nested_call['value'] = named_parameters['values'][i]
                if 'signatures' in named_parameters:
                    if named_parameters['signatures'][i] != '':
                        nested_call['signature'] = named_parameters[
                            'signatures'
                        ][i]
                nested_calls.append(nested_call)

            # gather non-nested parameters
            non_nested_parameters = [
                n
                for n, name in enumerate(named_parameters)
                if name not in ['targets', 'calldatas', 'values', 'signatures']
            ]

        elif (
            named_parameters is not None
            and 'targets' in named_parameters
            and 'payloads' in named_parameters
            and 'values' in named_parameters
        ):
            nested_calls = [
                {
                    'address': target,
                    'call_data': payload,
                    'value': value,
                    'signature': None,
                }
                for target, payload, value in zip(
                    named_parameters['targets'],
                    named_parameters['payloads'],
                    named_parameters['values'],
                )
            ]

            # gather non-nested parameters
            non_nested_parameters = [
                n
                for n, name in enumerate(named_parameters)
                if name not in ['targets', 'payloads', 'values']
            ]

        else:
            raise Exception('could not detect nested calls')

    # print non nested parameters
    if len(non_nested_parameters) > 0:
        print()
        toolstr.print_header('Call Parameters', style=styles['title'])
        input_names = evm.get_function_parameter_names(function_abi)
        for p, parameter in enumerate(decoded['parameters']):
            if p not in non_nested_parameters:
                parameter = '\[nested parameter, see below]'  # type: ignore
            input_name = input_names[p]
            if input_name is None:
                input_name = function_abi['inputs'][p]['type']
            if isinstance(parameter, tuple):
                print_bullet(
                    str(input_name),
                    indent=indent,
                    bullet=str(p + 1) + '.',
                )
                for subparameter in parameter:
                    if isinstance(subparameter, bytes):
                        subparameter = evm.binary_convert(
                            subparameter, 'prefix_hex'
                        )
                    toolstr.print(
                        indent + '    ' + stringify(subparameter),
                        style=styles['description'],
                    )
                if len(parameter) == 0:
                    toolstr.print(
                        indent + '    \[none]', style=styles['comment']
                    )
            else:
                if isinstance(parameter, bytes):
                    parameter = evm.binary_convert(parameter, 'prefix_hex')
                print_bullet(
                    input_name,
                    parameter,
                    indent=indent,
                    bullet=str(p + 1) + '.',
                )

    # print nested calls
    if nested:
        for nc, nested_call in enumerate(nested_calls):
            # nested_address, nested_call_data = nested_call
            title = (
                'Nested Call Data '
                + str(nc + 1)
                + ' / '
                + str(len(nested_calls))
            )
            print()
            await async_decode_call_command(
                args=[nested_call['address'], nested_call['call_data']],
                nested=False,
                title=title,
                indent='',
                mention_nested=False,
                send_value=nested_call['value'],
                explicit_signature=nested_call['signature'],
            )
            if nc + 1 != len(nested_calls):
                print()

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
