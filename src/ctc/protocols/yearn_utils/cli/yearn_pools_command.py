from __future__ import annotations

import toolcli

from ctc.protocols import yearn_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_yearn_pools_command,
        'help': 'display summary of yearn pools',
        'args': [
            {
                'name': '--sort',
                'help': 'pool field to sort by',
            },
            {
                'name': '-n',
                'help': 'number of pools to display',
                'type': int,
                'default': 20,
            },
            {
                'name': '--min-apy',
                'help': 'filter pools by minimum APY',
                'type': float,
            },
            {
                'name': '--min-apr',
                'help': 'filter pools by minimum APR',
                'type': float,
            },
            {
                'name': '--min-tvl',
                'help': 'filter pools by minimum TVL',
                'type': float,
            },
        ],
        'examples': [
            '',
            '--min-tvl 1000000',
            '--sort TVL',
        ],
    }


async def async_yearn_pools_command(
    *,
    sort: str | None,
    n: int | None,
    min_apy: float | None,
    min_apr: float | None,
    min_tvl: float | None,
) -> None:

    await yearn_utils.async_summarize_pools(
        sort_by=sort,
        min_tvl=min_tvl,
        min_apy=min_apy,
        min_apr=min_apr,
        n=n,
    )
