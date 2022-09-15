from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_call_command,
        'help': 'output result of a call',
        'args': [
            {'name': 'address', 'help': 'address to point call toward'},
            {
                'name': 'function',
                'help': 'function name, 4byte selector, or ABI',
            },
            {'name': 'args', 'nargs': '*', 'help': 'function arguments'},
            {
                'name': ['--verbose', '-v'],
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
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0x18160ddd',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca \'{"name": "totalSupply", "inputs": [], "outputs": [{"type": "uint256"}]}\'',
        ],
    }


async def async_call_command(
    *,
    address: spec.Address,
    function: str,
    args: typing.Sequence[str],
    verbose: bool,
    from_address: spec.Address,
    block: str,
) -> None:
    import asyncio

    if block is not None:
        block_number = await evm.async_block_number_to_int(block)
    else:
        block_number = 'latest'

    address_task = asyncio.create_task(
        evm.async_resolve_address(address, block=block)
    )

    address = await address_task

    if verbose:
        styles = cli.get_cli_styles()
        toolstr.print_text_box('Performing eth_call', style=styles['title'])
        cli.print_bullet(
            key='to address',
            value=toolstr.add_style(address, styles['metavar']),
        )
        if block is not None:
            cli.print_bullet(key='block', value=block)
        if from_address is not None:
            cli.print_bullet(key='from address', value=from_address)
        cli.print_bullet(key='function', value=function)
        cli.print_bullet(key='arguments', value=args)
        print()
        toolstr.print('result =', style=styles['option'])

    function_abi = await evm.async_parse_function_str_abi(
        function,
        contract_address=address,
    )

    if len(args) != len(function_abi['inputs']):
        raise Exception('improper number of arguments for function')

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
