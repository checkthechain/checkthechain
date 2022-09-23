from __future__ import annotations

import typing
from typing_extensions import Literal

import toolcli

from .. import llama_yields


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_llama_pools_command,
        'help': 'output data about pools tracked by Defi Llama',
        'args': [
            {
                'name': '--chain',
                'help': 'filter pools by chain',
            },
            {
                'name': '--project',
                'help': 'filter pools by project',
            },
            {
                'name': '--stablecoin',
                'action': 'store_true',
                'help': 'filter pools by whether they are stablecoin-based',
            },
            {
                'name': '--non-stablecoin',
                'action': 'store_true',
                'help': 'filter pools by whether they are not stablecoin-based',
            },
            {
                'name': '--single',
                'action': 'store_true',
                'help': 'filter pools by whether they use a single asset',
            },
            {
                'name': '--multi',
                'action': 'store_true',
                'help': 'filter pools by whether they use a multiple assets',
            },
            {
                'name': '--min-apy',
                'type': float,
                'help': 'filter pools by minimum yield rate',
            },
            {
                'name': '--max-apy',
                'type': float,
                'help': 'filter pools by maximum yield rate',
            },
            {
                'name': '--min-tvl',
                'type': float,
                'help': 'filter pools by miniumum TVL',
            },
            {
                'name': '--max-tvl',
                'type': float,
                'help': 'filter pools by maximum TVL',
            },
            {
                'name': '-n',
                'type': int,
                'help': 'number of pools to display',
            },
            {
                'name': ['-v', '--verbose'],
                'action': 'store_true',
                'help': 'display additional information',
            },
            {
                'name': '--show-id',
                'action': 'store_true',
                'help': 'show id of each pool in table',
            },
        ],
        'examples': [
            '',
            '--min-tvl 1000000',
            '--stablecoin',
            '--chain Ethereum',
            '--min-tvl 1000000 --min-apy 10 --chain Ethereum',
        ],
    }


async def async_llama_pools_command(
    *,
    chain: str | None,
    project: str | None,
    stablecoin: bool,
    non_stablecoin: bool,
    single: bool,
    multi: bool,
    min_apy: typing.SupportsFloat | None = None,
    max_apy: typing.SupportsFloat | None = None,
    min_tvl: typing.SupportsFloat | None = None,
    max_tvl: typing.SupportsFloat | None = None,
    n: int = 10,
    verbose: bool = False,
    show_id: bool = False,
) -> None:

    if single:
        exposure: typing.Optional[Literal['single', 'multi']] = 'single'
    elif multi:
        exposure = 'multi'
    else:
        exposure = None

    if stablecoin:
        use_stablecoin: bool | None = True
    elif non_stablecoin:
        use_stablecoin = False
    else:
        use_stablecoin = None

    await llama_yields.async_print_llama_pools_summary(
        chain=chain,
        project=project,
        stablecoin=use_stablecoin,
        exposure=exposure,
        min_apy=min_apy,
        max_apy=max_apy,
        min_tvl=min_tvl,
        max_tvl=max_tvl,
        n=n,
        verbose=verbose,
        show_id=show_id,
    )
