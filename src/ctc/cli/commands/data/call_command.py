from __future__ import annotations

import typing

import toolcli

from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_call_command,
        'help': 'output result of a call',
        'args': [
            {'name': 'address', 'help': 'address to point call toward'},
            {'name': 'function-name', 'help': 'name of function to call'},
            {'name': 'args', 'nargs': '*', 'help': 'function arguments'},
            {
                'name': '--verbose',
                'action': 'store_true',
                'help': 'show summary',
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
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca totalSupply',
        ],
    }


async def async_call_command(
    address: spec.Address,
    function_name: str,
    args: typing.Sequence[str],
    verbose: bool,
    from_address: spec.Address,
    block: str,
) -> None:
    import asyncio

    address_task = asyncio.create_task(
        evm.async_resolve_address(address, block=block)
    )

    if block is not None:
        block_number = await evm.async_block_number_to_int(block)
    else:
        block_number = 'latest'

    address = await address_task

    if verbose:
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

    function_abi = await evm.async_get_function_abi(
        contract_address=address,
        function_name=function_name,
    )

    if len(args) != len(function_abi['inputs']):
        print('could not find appropriate function abi')

    # convert args as needed
    typed_args: list[typing.Any] = []
    for arg, arg_abi in zip(args, function_abi['inputs']):
        if arg.isnumeric() and 'int' in arg_abi['type']:
            typed_args.append(int(arg))
        else:
            typed_args.append(arg)

    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abi,
        function_parameters=typed_args,
        from_address=from_address,
        block_number=block_number,
    )
    print(result)
