"""WIP
Desired Information
- token creation date
- holders
    - top token holders
    - number of holders
- token dex summary on major exchanges
    - volume
    - liquidity and liquidity depth
- token CEX activity and inflow/outflow
- how each of these values change over time
- available oracles
"""

from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_erc20_command,
        'help': 'display information about ERC20',
        'args': [
            {
                'name': 'erc20',
                'help': 'ERC20 address or symbol',
            },
        ],
        'examples': [
            'DAI',
            '0x6b175474e89094c44da98b954eedeac495271d0f',
        ],
    }


async def async_erc20_command(erc20: str) -> None:
    await evm.async_print_erc20_summary(erc20)
