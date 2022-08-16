from __future__ import annotations

import toolcli
import toolstr

from ctc import evm
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
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
        'examples': [
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0x9928e4046d7c6513326ccea028cd3e7a91c7590a',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0x9928e4046d7c6513326ccea028cd3e7a91c7590a --raw',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca 0x9928e4046d7c6513326ccea028cd3e7a91c7590a --block 14000000',
        ],
    }


async def async_balance_command(
    *,
    erc20_address: spec.Address,
    wallet_address: spec.Address,
    block: str,
    raw: bool,
) -> None:
    erc20_address = await evm.async_resolve_address(erc20_address, block=block)
    wallet_address = await evm.async_resolve_address(
        wallet_address,
        block=block,
    )
    balance = await evm.async_get_erc20_balance(
        wallet=wallet_address,
        token=erc20_address,
        block=block,
        normalize=(not raw),
    )
    if raw:
        print(balance)
    else:
        print(toolstr.format(balance))
