import asyncio

import toolstr
import tooltable

from ctc import evm
from ctc import rpc
from ctc.protocols import fei_utils


def get_command_spec():
    return {
        'f': async_pcv_deposits_command,
    }


async def async_pcv_deposits_command():
    await async_print_pcv_deposits()
    await rpc.async_close_http_session()


async def async_print_pcv_deposits():
    tokens_deposits = await fei_utils.async_get_tokens_deposits()

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
        evm.async_get_erc20s_symbols(pcv_tokens)
    )

    # get deposit balances
    deposit_tasks = []
    for token, deposits in non_fei_deposits.items():
        deposit_task = asyncio.create_task(
            fei_utils.async_get_deposits_resistant_balances_and_fei(deposits)
        )
        deposit_tasks.append(deposit_task)

    # token prices
    token_prices_list = await fei_utils.async_get_tokens_prices(
        tokens=pcv_tokens
    )
    token_prices = dict(zip(pcv_tokens, token_prices_list))

    # await results
    symbols = await symbols_task
    deposit_balances = dict(
        zip(non_fei_deposits.keys(), (await asyncio.gather(*deposit_tasks)))
    )

    dex_pools = {}
    for key, value in fei_utils.dex_pools.items():
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
                name = fei_utils.dex_pools[deposit]['name']
            if deposit in fei_utils.deposit_metadata:
                name = fei_utils.deposit_metadata[deposit]['name']
            if deposit in fei_utils.deposit_names:
                name = fei_utils.deposit_names[deposit]

            row = []
            row.append(symbols[t])
            row.append(balance_usd)
            row.append(name)
            row.append(deposit)
            rows.append(row)

    headers = [
        'asset',
        'balance',
        'address',
        'name',
    ]
    tooltable.print_table(rows, headers=headers)
    print()

