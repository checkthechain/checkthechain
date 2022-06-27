from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_balance_command,
        'help': 'output ETH balance of address',
        'args': [
            {'name': 'address', 'help': 'address of wallet'},
            {'name': '--block', 'help': 'block number'},
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'skip normalizing balance by 1e18 decimals',
            },
        ],
        'examples': [
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 --raw',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 --block 14000000',
        ],
    }


async def async_balance_command(
    *,
    address: str,
    block: typing.Optional[spec.BlockNumberReference],
    raw: bool,
) -> None:

    address = await evm.async_resolve_address(address, block=block)

    if block is not None:
        block = await evm.async_block_number_to_int(block)

    balance = await evm.async_get_eth_balance(
        address=address,
        block=block,
        normalize=(not raw),
    )
    if raw:
        print(balance)
    else:
        print(toolstr.format(balance))
