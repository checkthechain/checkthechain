from __future__ import annotations

import toolstr

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_balance_command,
        'help': 'output an ERC20 balance',
        'args': [
            {'name': 'erc20_address', 'help': 'address of ERC20 token'},
            {'name': 'wallet_address', 'help': 'address of wallet'},
            {'name': '--block', 'help': 'block number'},
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'whether to normalize balance by ERC20 decimals',
            },
        ],
    }


async def async_balance_command(erc20_address, wallet_address, block, raw):
    balance = await evm.async_get_erc20_balance_of(
        address=wallet_address,
        token=erc20_address,
        block=block,
        normalize=(not raw),
    )
    if raw:
        print(balance)
    else:
        print(toolstr.format(balance))
    await rpc.async_close_http_session()

