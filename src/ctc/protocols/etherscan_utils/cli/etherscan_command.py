from __future__ import annotations

import toolcli

from ctc.protocols import etherscan_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_etherscan_command,
        'args': [
            {
                'name': 'query',
                'help': 'address / tx / block / ERC20 symbol / ens',
            },
            {
                'name': '--holdings',
                'help': 'open page viewing holdings of address',
                'action': 'store_true',
            },
            {
                'name': '--erc20-transfers',
                'help': 'open page viewing ERC20 transfers of address',
                'action': 'store_true',
            },
            {
                'name': '--internal',
                'help': 'open page viewing internal txs of address',
                'action': 'store_true',
            },
            {
                'name': '--holders',
                'help': 'open page viewing holders of ERC20 address',
                'action': 'store_true',
            },
            {
                'name': '--logs',
                'help': 'open page viewing logs of transaction',
                'action': 'store_true',
            },
            {
                'name': '--changes',
                'help': 'open page viewing state changes of transaction',
                'action': 'store_true',
            },
            {
                'name': '--abi',
                'help': 'output only the json ABI of an address',
                'action': 'store_true',
            },
        ],
        'help': 'open etherscan query in browser or fetch',
        'examples': {
            '0xd3181ddbb2cea7b4954b8d4a05dbf85d8fc36aef': {'skip': True},
            '0x146063226f2bc60ab02fff825393555672ff505afb352ff11b820355422ba31e': {
                'skip': True
            },
            '14000000': {'skip': True},
            'vitalik.eth': {'skip': True},
            'vitalik.eth --holdings': {'skip': True},
            'vitalik.eth --erc20-transfers': {'skip': True},
            'DAI': {'skip': True},
            'DAI --holders': {'skip': True},
        },
    }


async def async_etherscan_command(
    *,
    query: str,
    logs: bool,
    changes: bool,
    holdings: bool,
    erc20_transfers: bool,
    internal: bool,
    holders: bool,
    abi: bool,
) -> None:

    await etherscan_utils.async_open_etherscan_in_browser(
        query=query,
        logs=logs,
        changes=changes,
        holdings=holdings,
        erc20_transfers=erc20_transfers,
        internal=internal,
        holders=holders,
        abi=abi,
    )

