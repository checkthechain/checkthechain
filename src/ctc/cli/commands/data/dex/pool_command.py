from __future__ import annotations

import asyncio
import typing

import toolcli
import toolstr
import tooltime

from ctc import cli
from ctc.cli import cli_utils
from ctc import evm
from ctc import config
from ctc import spec
from ctc.toolbox.defi_utils import dex_utils


help_message = """show information about a pool"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_dex_pool_command,
        'help': help_message,
        'args': [
            {
                'name': 'pool',
                'help': 'address of pool',
            },
            {
                'name': '--network',
                'help': 'network to query',
            },
            {
                'name': '--block',
                'help': 'block number',
            },
        ],
        'examples': [
            '0xc5be99a02c6857f9eac67bbce58df5572498f40c',
            '0xc5be99a02c6857f9eac67bbce58df5572498f40c --block 14000000',
        ],
    }


async def async_dex_pool_command(
    *,
    pool: spec.Address,
    network: str | int | None,
    block: str | None,
) -> None:
    from ctc import db

    if network is not None:
        network = cli_utils.parse_network(typing.cast(str, network))
    if network is None:
        network = config.get_default_network()

    if block is not None:
        block_number = await cli_utils.async_parse_block(block)
    else:
        block_number = None

    dex_pool = await db.async_query_dex_pool(address=pool, network=network)
    if dex_pool is None:
        print('pool not found, updating dex database')
        await dex_utils.async_update_all_dexes()
        dex_pool = await db.async_query_dex_pool(address=pool, network=network)
        if dex_pool is None:
            raise Exception('could not find pool data')

    dex = await dex_utils.async_get_dex_class(
        pool=dex_pool['address'],
    )

    # queue creation timestamp task
    creation_timestamp_coroutine = evm.async_get_block_timestamp(
        dex_pool['creation_block'],
    )
    creation_timestamp_task = asyncio.create_task(creation_timestamp_coroutine)

    # queue asset symbols task
    assets: typing.Sequence[str] = [
        typing.cast(str, dex_pool.get(key))
        for key in ['asset0', 'asset1', 'asset2', 'asset3']
        if dex_pool.get(key) is not None
    ]
    asset_symbols_task = asyncio.create_task(
        evm.async_get_erc20s_symbols(assets)
    )

    # queue balances task
    balances_coroutine = dex.async_get_pool_balances(
        pool,
        network=network,
        block=block_number,
    )
    balances_task = asyncio.create_task(balances_coroutine)

    # await all tasks
    creation_timestamp = await creation_timestamp_task
    asset_symbols = await asset_symbols_task
    balances = await balances_task

    # print bullet
    styles = cli.get_cli_styles()
    toolstr.print_text_box('Pool Summary', style=styles['title'])
    cli.print_bullet(
        key='pool',
        value=toolstr.add_style(dex_pool['address'], styles['metavar']),
    )
    cli.print_bullet(
        key='factory',
        value=toolstr.add_style(dex_pool['factory'], styles['metavar']),
    )
    dex_name = dex.get_dex_name()
    cli.print_bullet(key='DEX', value=dex_name)
    cli.print_bullet(key='creation block', value=dex_pool['creation_block'])
    cli.print_bullet(
        key='creation timestamp',
        value=tooltime.timestamp_to_iso_pretty(creation_timestamp),
    )
    cli.print_bullet(key='fee', value=dex_pool['fee'])
    cli.print_bullet(key='assets', value='')

    rows = []
    for a in range(len(assets)):
        row = [assets[a], asset_symbols[a], balances[assets[a]]]
        rows.append(row)
    labels = [
        'address',
        'symbol',
        'balance',
    ]
    toolstr.print_table(
        rows,
        labels=labels,
        indent=4,
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'address': styles['metavar'],
            'symbol': styles['option'],
            'balance': styles['description'],
        },
        column_formats={
            'balance': {'trailing_zeros': True},
        },
    )

    if dex_name == 'UniswapV2':
        from ctc.protocols import uniswap_v2_utils
        from ctc.toolbox.defi_utils.dex_utils.amm_utils import cpmm

        print()
        toolstr.print_header('Pool State', style=styles['title'])
        tokens_metadata = await uniswap_v2_utils.async_get_pool_tokens_metadata(
            pool
        )
        x_symbol = tokens_metadata['x_symbol']
        y_symbol = tokens_metadata['y_symbol']
        pool_state = await uniswap_v2_utils.async_get_pool_state(
            pool,
            block=block_number,
        )
        cpmm.print_pool_summary(
            x_name=x_symbol,
            y_name=y_symbol,
            **pool_state,
        )
