"""
the implementations here are stopgap solutions
- in future will create a more complete internal Uniswap v3 representation
"""
from __future__ import annotations

import typing

from ctc.toolbox import optimize_utils
from ctc import evm

from . import contracts


async def async_get_liquidity_depth(
    *,
    new_price: int | float,
    token_in: str,
    token_out: str,
    fee: int,
    min_search_depth: int = 1,
    max_search_depth: int = int(10e6 * 1e18),
    verbose: bool = False,
    output_tol: int | float | None = None,
    input_tol: int | float | None = None,
    max_iterations: int = 50,
    token_in_decimals: int | None = None,
    token_out_decimals: int | None = None,
) -> float:
    """return amount of token sold needed to reach new price"""

    if token_in_decimals is None:
        token_in_decimals = await evm.async_get_erc20_decimals(token_in)
    if token_out_decimals is None:
        token_out_decimals = await evm.async_get_erc20_decimals(token_out)

    if input_tol is None:
        input_tol = 10 ** (token_in_decimals - 2)

    swap_kwargs = {
        'token_in': token_in,
        'token_out': token_out,
        'fee': fee,
        'token_in_decimals': token_in_decimals,
        'token_out_decimals': token_out_decimals,
    }
    f_kwargs = {
        'target_new_price': new_price,
        'swap_kwargs': swap_kwargs,
    }

    try:
        return await optimize_utils.async_bisect(
            async_f=_async_new_price_distance,
            a=int(min_search_depth),
            b=int(max_search_depth),
            max_iterations=max_iterations,
            output_tol=output_tol,
            input_tol=input_tol,
            f_kwargs=f_kwargs,
            verbose=verbose,
        )
    except optimize_utils.BadSearchDomain:
        return 0


async def _async_new_price_distance(
    amount_sold: int | float,
    *,
    target_new_price: float,
    swap_kwargs: typing.Any,
) -> float:
    actual_new_price = await async_get_new_price(
        amount_sold=amount_sold, **swap_kwargs
    )
    return actual_new_price - target_new_price


async def async_get_new_price(
    *,
    amount_sold: int | float,
    token_in: str,
    token_out: str,
    fee: int,
    token_in_decimals: int,
    token_out_decimals: int,
    probe_amount_sold: int | None = None,
) -> float:
    """return new price in pool after a given amount of a token is sold

    - does this by computing a trade and an additional probe trade
    """
    if probe_amount_sold is None:
        probe_amount_sold = 10 ** token_in_decimals

    out_to_in = typing.cast(int, 10 ** (token_in_decimals - token_out_decimals))

    amount_sold = int(amount_sold)
    total_input_probe = int(amount_sold + probe_amount_sold)

    bought_amount = await contracts.async_quote_exact_input_single(
        token_in=token_in,
        token_out=token_out,
        fee=fee,
        amount_in=amount_sold,
        sqrt_price_limit_x96=0,
    )
    probe_amount_bought = await contracts.async_quote_exact_input_single(
        token_in=token_in,
        token_out=token_out,
        fee=fee,
        amount_in=total_input_probe,
        sqrt_price_limit_x96=0,
    )

    if not isinstance(bought_amount, int):
        raise Exception('invalid rpc result')
    if not isinstance(probe_amount_bought, int):
        raise Exception('invalid rpc result')

    probe_price = (
        out_to_in * (probe_amount_bought - bought_amount) / probe_amount_sold
    )

    return probe_price
