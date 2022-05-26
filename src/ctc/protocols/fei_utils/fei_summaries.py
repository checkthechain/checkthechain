from __future__ import annotations

import typing

import toolstr

from ctc import evm
from ctc import spec

from . import analytics
from . import coracle


async def async_print_pcv_assets(
    block: spec.BlockNumberReference | None = None,
) -> None:
    import asyncio

    if block is not None:
        if isinstance(block, str) and block.isnumeric():
            block = int(block)

    tokens_deposits = await coracle.async_get_tokens_deposits(block=block)

    non_fei_deposits = {
        k: v
        for k, v in tokens_deposits.items()
        if k
        not in [
            '0x1111111111111111111111111111111111111111',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        ]
    }
    pcv_tokens = list(non_fei_deposits.keys())
    symbols_task = asyncio.create_task(
        evm.async_get_erc20s_symbols(pcv_tokens, block=block)
    )

    # get deposit balances
    deposit_tasks = []
    for token, deposits in non_fei_deposits.items():
        deposit_task = asyncio.create_task(
            coracle.async_get_deposits_resistant_balances_and_fei(
                deposits, block=block
            )
        )
        deposit_tasks.append(deposit_task)

    # token prices
    token_prices_list = await coracle.async_get_tokens_prices(
        tokens=pcv_tokens,
        block=block,
    )
    token_prices = dict(zip(pcv_tokens, token_prices_list))

    # await results
    symbols = await symbols_task
    deposit_balances = dict(
        zip(non_fei_deposits.keys(), (await asyncio.gather(*deposit_tasks)))
    )

    # get token totals
    token_totals = {}
    token_totals_usd = {}
    for token, token_balances in deposit_balances.items():
        token_totals[token] = (
            sum([balance[0] for balance in token_balances]) / 1e18
        )
        token_totals_usd[token] = token_prices[token] * token_totals[token]

    toolstr.print_text_box('Fei PCV Assets')

    # total for each token
    rows = []
    labels = [
        'asset',
        'amount',
        # 'deposits',
        'price',
        'total',
    ]
    for symbol, token in zip(symbols, pcv_tokens):
        row = [
            symbol,
            toolstr.format(token_totals[token], order_of_magnitude=True),
            # len(tokens_deposits[token]),
            toolstr.format(
                token_prices[token],
                prefix='$',
                decimals=2,
                trailing_zeros=True,
            ),
            toolstr.format(
                token_totals_usd[token],
                prefix='$',
                decimals=2,
                trailing_zeros=True,
                order_of_magnitude=True,
            ),
        ]
        rows.append(row)

    total_usd = toolstr.format(
        sum(token_totals_usd.values()),
        prefix='$',
        decimals=2,
        trailing_zeros=True,
        order_of_magnitude=True,
    )
    print('total', total_usd)
    print()
    toolstr.print_table(rows, labels=labels)


async def async_print_pcv_deposits(
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> None:
    import asyncio

    if block is not None:
        block = await evm.async_block_number_to_int(block=block)

    tokens_deposits = await coracle.async_get_tokens_deposits(block=block)

    non_fei_deposits = {
        k: v
        for k, v in tokens_deposits.items()
        if k
        not in [
            '0x1111111111111111111111111111111111111111',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        ]
    }
    pcv_tokens = list(non_fei_deposits.keys())
    symbols_task = asyncio.create_task(
        evm.async_get_erc20s_symbols(pcv_tokens, block=block)
    )

    # fei balances
    fei_deposits = await coracle.async_get_token_deposits(
        '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        block=block,
    )
    fei_balances_task = asyncio.create_task(
        coracle.async_get_deposits_balances(fei_deposits, block=block)
    )

    # get deposit balances
    deposit_tasks = []
    for token, deposits in non_fei_deposits.items():
        coroutine = coracle.async_get_deposits_resistant_balances_and_fei(
            deposits, block=block
        )
        deposit_task = asyncio.create_task(coroutine)
        deposit_tasks.append(deposit_task)

    # token prices
    token_prices_list = await coracle.async_get_tokens_prices(
        tokens=pcv_tokens,
        block=block,
    )
    token_prices = dict(zip(pcv_tokens, token_prices_list))

    # await results
    symbols = await symbols_task
    deposit_balances = dict(
        zip(non_fei_deposits.keys(), (await asyncio.gather(*deposit_tasks)))
    )

    dex_pools = {}
    for key, value in analytics.dex_pools.items():
        dex_pools[value['address']] = dict(value)
        dex_pools[value['address']]['name'] = key

    toolstr.print_text_box('FEI PCV Deposits')
    rows = []
    for t, token in enumerate(pcv_tokens):
        for deposit, balance in zip(
            tokens_deposits[token], deposit_balances[token]
        ):

            balance_usd = token_prices[token] * balance[0] / 1e18
            balance_usd = toolstr.format(
                balance_usd,
                prefix='$',
                trailing_zeros=True,
                decimals=2,
                order_of_magnitude=True,
            )

            name = ''
            if deposit in dex_pools:
                deposit_metadata = analytics.dex_pools[deposit]
                name = (
                    deposit_metadata['platform']
                    + ' '
                    + 'FEI-'
                    + '-'.join(deposit_metadata['other_assets'])
                )
            if deposit in coracle.deposit_metadata:
                name = coracle.deposit_metadata[deposit]['name']
            if deposit in coracle.deposit_names:
                name = coracle.deposit_names[deposit]

            row = []
            row.append(symbols[t])
            row.append(balance_usd)
            row.append(name)
            row.append(deposit)
            rows.append(row)

    labels = [
        'asset',
        'balance',
        'name',
        'address',
    ]
    toolstr.print_table(rows, labels=labels)
    print()

    toolstr.print_text_box('FEI Deployments')

    fei_balances = await fei_balances_task

    rows = []
    for address, fei_balance in zip(fei_deposits, fei_balances):
        name = ''
        if address in coracle.deposit_metadata:
            name = coracle.deposit_metadata[address]['name']
        if address in coracle.deposit_names:
            name = coracle.deposit_names[address]
        row = [
            'FEI',
            toolstr.format(
                fei_balance / 1e18,
                order_of_magnitude=True,
                trailing_zeros=True,
                decimals=2,
                prefix='$',
            ),
            name,
            address,
        ]
        rows.append(row)
    labels = ['asset', 'balance', 'name', 'address']
    toolstr.print_table(rows, labels=labels)
