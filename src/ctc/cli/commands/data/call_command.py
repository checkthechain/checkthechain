from __future__ import annotations

from ctc import rpc
from ctc import evm


def get_command_spec():
    return {
        'f': async_call_command,
        'help': 'output result of a call',
        'args': [
            {'name': 'address', 'help': 'address to point call toward'},
            {'name': 'function-name', 'help': 'name of function to call'},
            {'name': 'args', 'nargs': '*', 'help': 'function arguments'},
            {
                'name': '--quiet',
                'action': 'store_true',
                'help': 'hide summary and only output function result',
            },
            {
                'name': '--from',
                'dest': 'from_address',
                'help': 'address where call should come from',
            },
            {
                'name': '--block',
                'help': 'block number for call',
            },
        ],
    }


async def async_call_command(address, function_name, args, quiet, from_address, block):

    if block is not None:
        block = await evm.async_block_number_to_int(block)

    if not quiet:
        print('performing eth_call')
        print('- to address:', address)
        if block is not None:
            print('- block:', block)
        if from_address is not None:
            print('- from address:', from_address)
        print('- function:', function_name)
        print('- arguments:', args)
        print()
        print('result:')

    result = await rpc.async_eth_call(
        to_address=address,
        function_name=function_name,
        function_parameters=args,
        from_address=from_address,
        block_number=block,
    )
    print(result)
    raise Exception()

    await rpc.async_close_http_session()

