"""
the implementations here are stopgap solutions
- in future will create a more complete internal Uniswap v3 representation
"""

from ctc.toolbox import optimize_utils
from ctc import evm

from .contracts import quoter


async def async_get_liquidity_depth(
    new_price,
    token_in,
    token_out,
    fee,
    min_search_depth=1,
    max_search_depth=int(10e6 * 1e18),
    verbose=False,
    output_tol=None,
    input_tol=None,
    max_iterations=50,
    token_in_decimals=None,
    token_out_decimals=None,
):
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


async def _async_new_price_distance(amount_sold, target_new_price, swap_kwargs):
    actual_new_price = await async_get_new_price(amount_sold, **swap_kwargs)
    return actual_new_price - target_new_price


async def async_get_new_price(
    amount_sold,
    token_in,
    token_out,
    fee,
    token_in_decimals,
    token_out_decimals,
    probe_amount_sold=None,
):
    """return new price in pool after a given amount of a token is sold

    - does this by computing a trade and an additional probe trade
    """
    if probe_amount_sold is None:
        probe_amount_sold = 10 ** token_in_decimals

    out_to_in = 10 ** (token_in_decimals - token_out_decimals)

    amount_sold = int(amount_sold)
    total_input_probe = int(amount_sold + probe_amount_sold)

    bought_amount = await quoter.async_quote_exact_input_single(
        token_in=token_in,
        token_out=token_out,
        fee=fee,
        amount_in=amount_sold,
        sqrt_price_limit_x96=0,
    )
    probe_amount_bought = await quoter.async_quote_exact_input_single(
        token_in=token_in,
        token_out=token_out,
        fee=fee,
        amount_in=total_input_probe,
        sqrt_price_limit_x96=0,
    )

    probe_price = (
        out_to_in * (probe_amount_bought - bought_amount) / probe_amount_sold
    )

    return probe_price

