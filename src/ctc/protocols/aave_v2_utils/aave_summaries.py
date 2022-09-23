from __future__ import annotations

import asyncio
import typing

import toolstr
import numpy as np

from ctc import evm
from ctc import spec
from . import aave_spec
from . import aave_interest_rates
from . import aave_oracle


async def async_print_aave_addresses(
    *,
    verbose: bool = False,
    block: spec.BlockNumberReference | None = None,
    max_width: int | None = None,
) -> None:

    from ctc import cli

    indent = 4

    styles = cli.get_cli_styles()

    toolstr.print_text_box('Aave V2 Addresses', style=styles['title'])

    network = 'mainnet'
    toolstr.print('network = ' + str(network), style=styles['comment'])

    # print general contracts
    contracts = [
        'PriceOracle',
        'LendingPoolProvider',
        'LendingPool',
        'IncentivesController',
        'Collector',
    ]
    rows = []
    for contract in contracts:
        address = aave_spec.get_aave_address(contract, network=network)
        row = [contract, address]
        rows.append(row)
    print()
    if max_width is not None:
        max_table_width = max_width - indent
    else:
        max_table_width = None
    toolstr.print_table(
        rows,
        indent=indent,
        border=styles['comment'],
        column_styles=[styles['option'], styles['metavar']],
        max_table_width=max_table_width,
    )

    # print token markets
    token_markets = await aave_interest_rates.async_get_token_markets(
        block=block
    )

    print()
    print()
    toolstr.print_header('Token Markets', style=styles['title'])
    print()
    if verbose:

        rows = []
        for token_market in token_markets:
            address_labels = [
                'underlying',
                'atoken',
                'variable debt',
                'stable debt',
                'interest rate',
            ]
            addresses = [
                token_market['underlying'],
                token_market['reserve_data']['atoken_address'],
                token_market['reserve_data']['variable_debt_token_address'],
                token_market['reserve_data']['stable_debt_token_address'],
                token_market['reserve_data']['interest_rate_strategy_address'],
            ]
            address_pieces = [
                toolstr.add_style(label, styles['comment'])
                + ' '
                + toolstr.add_style(address, styles['metavar'])
                for label, address in zip(address_labels, addresses)
            ]

            row = [token_market['symbol'], '\n'.join(address_pieces)]
            rows.append(row)
        labels = [
            'symbol',
            'addresses',
        ]

        rows = sorted(rows, key=lambda row: row[0])

        toolstr.print_multiline_table(
            rows,
            indent=indent,
            labels=labels,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'symbol': styles['option'],
            },
            max_table_width=max_table_width,
        )

    else:
        rows = []
        for token_market in token_markets:
            row = [
                token_market['symbol'],
                token_market['reserve_data']['atoken_address'],
            ]
            rows.append(row)
        labels = [
            'symbol',
            'atoken',
        ]

        rows = sorted(rows, key=lambda row: row[0])

        toolstr.print_table(
            rows,
            indent=indent,
            labels=labels,
            border=styles['comment'],
            label_style=styles['title'],
            column_styles={
                'symbol': styles['option'],
                'atoken': styles['metavar'],
            },
            max_table_width=max_table_width,
        )


async def async_print_token_markets_summary(
    *,
    verbose: bool = False,
    block: spec.BlockNumberReference | None = None,
    max_width: int | None = None,
) -> None:

    from ctc import cli

    if block is None:
        block = 'latest'

    token_markets = await aave_interest_rates.async_get_token_markets(
        block=block
    )

    total_supplies_coroutine = evm.async_get_erc20s_total_supplies(
        [
            token_market['reserve_data']['atoken_address']
            for token_market in token_markets
        ],
        block=block,
    )
    total_supplies_task = asyncio.create_task(total_supplies_coroutine)

    coroutines = [
        aave_interest_rates.async_get_interest_rates(
            reserve_data=token_market['reserve_data'],
            block=block,
        )
        for token_market in token_markets
    ]
    interest_rates_task = asyncio.gather(*coroutines)

    reserves_list = [
        token_market['underlying'] for token_market in token_markets
    ]
    prices_coroutine = aave_oracle.async_get_asset_prices(
        reserves_list, block=block
    )
    prices_task = asyncio.create_task(prices_coroutine)

    reserve_balances_coroutines = [
        evm.async_get_erc20_balance(
            wallet=token_market['reserve_data']['atoken_address'],
            token=token_market['underlying'],
            block=block,
        )
        for token_market in token_markets
    ]
    reserve_balances = await asyncio.gather(*reserve_balances_coroutines)

    interest_rates = await interest_rates_task
    prices = await prices_task
    total_supplies = await total_supplies_task

    rows = []
    tvls = []
    tvbs = []
    for r in range(len(token_markets)):
        supply_apy = interest_rates[r]['supply_apy']
        borrow_apy = interest_rates[r]['borrow_apy']
        total_supply = total_supplies[r]
        tvl = total_supply * prices[r]
        tvls.append(tvl)

        liquidity = reserve_balances[r]
        tvb = tvl - liquidity * prices[r]
        tvbs.append(tvb)

        row = [
            token_markets[r]['symbol'],
            supply_apy,
            borrow_apy,
            tvl,
            tvb,
        ]
        if verbose:
            row.append(tvb / tvl)
            row.append(prices[r])
        rows.append(row)

    labels = [
        'token',
        'supply APY',
        'borrow APY',
        'TVL',
        'TVB',
    ]
    if verbose:
        labels.append('util %')
        labels.append('price')

    # sort rows
    sort_by = [
        #     'supply APY',
        'TVL',
    ]
    sort_indices = [labels.index(column) for column in sort_by]
    ascending = False
    rows = sorted(
        rows,
        reverse=(not ascending),
        key=lambda row: tuple(row[index] for index in sort_indices),
    )

    # special formatting
    oom_columns = [
        'supply APY',
        'borrow APY',
    ]
    for row in rows:
        for column in oom_columns:
            index = labels.index(column)
            item = row[index]
            if item > 100:
                item = toolstr.format(item * 100, order_of_magnitude=True) + '%'
                row[index] = item

    rows.append([''] * len(labels))
    total_row = [
        'TOTAL',
        '',
        '',
        toolstr.format(
            sum(tvls),
            order_of_magnitude=True,
            decimals=2,
            trailing_zeros=True,
            prefix='$',
        ),
        toolstr.format(
            sum(tvbs),
            order_of_magnitude=True,
            decimals=2,
            trailing_zeros=True,
            prefix='$',
        ),
    ]
    if verbose:
        total_row.extend(['', ''])
    total_row = [toolstr.add_style(cell, 'bold') for cell in total_row]
    rows.append(total_row)

    styles = cli.get_cli_styles()
    toolstr.print_text_box('Aave V2 Markets', style=styles['title'])
    print()
    toolstr.print_table(
        rows,
        labels=labels,
        column_formats={
            'supply APY': {
                'percentage': True,
                'trailing_zeros': True,
                'decimals': 3,
            },
            'borrow APY': {
                'percentage': True,
                'trailing_zeros': True,
                'decimals': 3,
            },
            'TVL': {
                'order_of_magnitude': True,
                'trailing_zeros': True,
                'prefix': '$',
                'decimals': 2,
            },
            'TVB': {
                'order_of_magnitude': True,
                'trailing_zeros': True,
                'prefix': '$',
                'decimals': 2,
            },
            'util %': {
                'percentage': True,
                'trailing_zeros': True,
                'decimals': 2,
            },
            'price': {
                'prefix': '$',
                'trailing_zeros': True,
                'decimals': 2,
            },
        },
        border=styles['comment'],
        label_style=styles['title'],
        column_styles={
            'token': styles['metavar'],
            'supply APY': styles['description'],
            'borrow APY': styles['description'],
            'TVL': styles['description'],
            'TVB': styles['description'],
            'util %': styles['description'],
            'price': styles['description'],
        },
        max_table_width=max_width,
    )
    print()
    toolstr.print('network = mainnet', style=styles['comment'])


async def async_print_token_market_summary(
    token: str | spec.Address,
    *,
    blocks: typing.Sequence[int],
    verbose: bool = False,
) -> None:

    from ctc import cli

    if not evm.is_address_str(token):
        token_address = await evm.async_get_erc20_address(token)
    else:
        token_address = token

    timestamps_task = asyncio.create_task(
        evm.async_get_block_timestamps(blocks)
    )

    reserve_data_by_block = (
        await aave_interest_rates.async_get_reserve_data_by_block(
            asset=token_address,
            blocks=blocks,
            provider={'chunk_size': 1},
        )
    )

    atoken_address = reserve_data_by_block['atoken_address'][0]

    interest_rates_task = asyncio.create_task(
        aave_interest_rates.async_get_interest_rates_by_block(
            token=token_address,
            blocks=blocks,
            reserve_data_by_block=reserve_data_by_block,
        )
    )

    # compute tvls
    total_supplies_task = asyncio.create_task(
        evm.async_get_erc20_total_supply_by_block(
            atoken_address,
            blocks=blocks,
        )
    )

    # compute tvbs
    balances_task = asyncio.create_task(
        evm.async_get_erc20_balance_by_block(
            wallet=atoken_address,
            token=token,
            blocks=blocks,
        )
    )

    total_supplies = await total_supplies_task
    total_supplies_array = np.array(total_supplies)
    prices_task = asyncio.create_task(
        aave_oracle.async_get_asset_price_by_block(
            token_address,
            blocks=blocks,
        )
    )

    prices = await prices_task
    prices_array = np.array(prices)
    tvls = total_supplies_array * prices_array

    balances = await balances_task
    balances_array = np.array(balances)
    tvbs = (total_supplies_array - balances_array) * prices_array

    if verbose:
        utilization = tvbs / tvls

    # compute interest rates
    interest_rates = await interest_rates_task
    supply_apy = np.array(interest_rates['supply_apy']) * 100
    borrow_apy = np.array(interest_rates['borrow_apy']) * 100

    styles = cli.get_cli_styles()
    toolstr.print_text_box(
        'Summary of ' + token + ' on Aave v2', style=styles['title']
    )

    percentage_kwargs = {
        'yaxis_kwargs': {
            'tick_label_format': {
                'postfix': '%',
                'decimals': 2,
                'trailing_zeros': True,
            }
        }
    }
    dollar_kwargs = {'yaxis_kwargs': {'tick_label_format': {'prefix': '$'}}}
    plots = [
        ('Supply APY', supply_apy, percentage_kwargs),
        ('Borrow APY', borrow_apy, percentage_kwargs),
        ('TVL', tvls, dollar_kwargs),
        ('TVB', tvbs, dollar_kwargs),
    ]
    if verbose:
        plots.append(('Utilization', utilization * 100, percentage_kwargs))
        plots.append(('Price', prices_array, dollar_kwargs))
    timestamps = await timestamps_task
    for title, data, plot_kwargs in plots:
        print()
        plot = toolstr.render_line_plot(
            xvals=timestamps,
            yvals=data,
            n_rows=40,
            n_columns=120,
            line_style=styles['description'],
            chrome_style=styles['comment'],
            tick_label_style=styles['metavar'],
            **plot_kwargs,  # type: ignore
        )
        toolstr.print(
            toolstr.hjustify(title, 'center', 70),
            indent=4,
            style=styles['title'],
        )
        print()
        toolstr.print(plot, indent=4)
        print()
        print()