from __future__ import annotations

import toolcli

from ctc.protocols import yearn_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_yearn_vaults_command,
        'help': 'display summary of Yearn vaults',
        'args': [
            {
                'name': 'query',
                'help': 'address or name of vault to show details of',
                'nargs': '?',
            },
            {
                'name': '--sort',
                'help': 'vault field to sort by',
            },
            {
                'name': '-n',
                'help': 'number of vaults to display',
                'type': int,
                'default': 20,
            },
            {
                'name': '--min-apy',
                'help': 'filter vaults by minimum APY',
                'type': float,
            },
            {
                'name': '--min-apr',
                'help': 'filter vaults by minimum APR',
                'type': float,
            },
            {
                'name': '--min-tvl',
                'help': 'filter vaults by minimum TVL',
                'type': float,
            },
            {
                'name': ['-v', '--verbose'],
                'help': 'output additional information',
                'action': 'store_true',
            },
            {
                'name': '--harvests',
                'help': 'show harvests when viewing individual vault',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            '--min-tvl 1000000',
            '--sort TVL',
            '0x9d409a0a012cfba9b15f6d4b36ac57a46966ab9a',
            '0x9d409a0a012cfba9b15f6d4b36ac57a46966ab9a -v',
            '0x9d409a0a012cfba9b15f6d4b36ac57a46966ab9a --harvests',
        ],
    }


async def async_yearn_vaults_command(
    *,
    query: str | None,
    sort: str | None,
    n: int | None,
    min_apy: float | None,
    min_apr: float | None,
    min_tvl: float | None,
    verbose: bool,
    harvests: bool,
) -> None:

    if query is not None:
        await yearn_utils.async_print_vault_summary(
            query=query,
            verbose=verbose,
            network='mainnet',
            show_harvests=harvests,
        )

    else:
        await yearn_utils.async_print_vaults_summary(
            sort_by=sort,
            min_tvl=min_tvl,
            min_apy=min_apy,
            min_apr=min_apr,
            n=n,
            verbose=verbose,
            network='mainnet',
        )
