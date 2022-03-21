from __future__ import annotations

import typing

import toolstr

from ctc import binary
from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_decode_command,
        'help': 'decode EVM call data',
        'args': [
            {'name': 'args', 'nargs': '+'},
        ],
    }


async def async_decode_command(args: typing.Sequence[str]):
    if len(args) == 1:
        from ctc.protocols import fourbyte_utils
        call_data = args[0]
        signature = call_data[:10]
        result = await fourbyte_utils.async_query_function_signature(signature)
        print(result)
        return
    elif len(args) == 2:
        contract_address, call_data = args
        contract_abi = await evm.async_get_contract_abi(contract_address=contract_address)
        decoded = binary.decode_call_data(
            contract_abi=contract_abi, call_data=call_data
        )
        function_abi = decoded['function_abi']

    toolstr.print_text_box('Decoding Call Data')
    print('- n_bytes:', len(binary.convert(call_data, 'binary')))
    print()

    toolstr.print_header('Function Info')
    print('- name:', function_abi['name'])
    print('- selector:', decoded['function_selector'])
    print('- signature:', binary.get_function_signature(function_abi))
    print('- inputs:')
    for p, parameter in enumerate(function_abi['inputs']):
        print('    ', str(p + 1) + '.', parameter['name'], parameter['type'])
    print('- outputs:')
    for p, parameter in enumerate(function_abi['outputs']):
        print('    ', str(p + 1) + '.', parameter['name'], parameter['type'])
    print()
    toolstr.print_header('Function Parameters')
    input_names = binary.get_function_parameter_names(function_abi)
    for p, parameter in enumerate(decoded['parameters']):
        if isinstance(parameter, tuple):
            print(str(p + 1) + '.', str(input_names[p]) + ':')
            for subparameter in parameter:
                print('    ' + str(subparameter))
        else:
            print(str(p + 1) + '.', str(input_names[p]) + ':', parameter)

    await rpc.async_close_http_session()

