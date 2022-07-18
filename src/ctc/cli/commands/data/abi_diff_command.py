from __future__ import annotations

import typing

from ctc import evm

if typing.TYPE_CHECKING:
    import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_abi_diff_command,
        'help': 'display diff of two contract ABI\'s',
        'args': [
            {
                'name': 'first_address',
                'help': 'first contract address',
            },
            {
                'name': 'second_address',
                'help': 'second contract address',
            },
            {
                'name': '--functions',
                'help': 'show functions only',
                'action': 'store_true',
            },
            {
                'name': '--events',
                'help': 'show events only',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419 0xf79d6afbb6da890132f9d7c355e3015f15f3406f',
        ],
    }


async def async_abi_diff_command(
    *,
    first_address: str,
    second_address: str,
    functions: bool,
    events: bool,
) -> None:
    first_abi = await evm.async_get_contract_abi(first_address)
    second_abi = await evm.async_get_contract_abi(second_address)
    evm.print_contract_abi_diff(
        first_contract_abi=first_abi,
        second_contract_abi=second_abi,
        first_name=first_address,
        second_name=second_address,
        functions_only=functions,
        events_only=events,
    )
