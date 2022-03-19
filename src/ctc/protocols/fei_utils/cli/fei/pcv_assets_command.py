import asyncio

import toolcli
import toolstr
import tooltable  # type: ignore

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.protocols import fei_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_pcv_assets_command,
        'help': 'output summary of Fei PCV assets',
        'args': [
            {'name': '--block', 'help': 'block number'},
        ],
    }


async def async_pcv_assets_command(block: str) -> None:
    await async_print_pcv_assets(block=block)
    await rpc.async_close_http_session()


async def async_print_pcv_assets(block: spec.BlockNumberReference) -> None:

    if block is not None:
        if isinstance(block, str) and block.isnumeric():
            block = int(block)

    tokens_deposits = await fei_utils.async_get_tokens_deposits(block=block)

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
            fei_utils.async_get_deposits_resistant_balances_and_fei(
                deposits, block=block
            )
        )
        deposit_tasks.append(deposit_task)

    # token prices
    token_prices_list = await fei_utils.async_get_tokens_prices(
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
    headers = [
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
    print()
    tooltable.print_table(rows, headers=headers)

