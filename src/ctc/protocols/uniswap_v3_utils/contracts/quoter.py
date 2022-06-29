from __future__ import annotations

from ctc import rpc
from ctc import spec

from .. import uniswap_v3_spec


async def async_quote_exact_input_single(
    token_in: spec.Address,
    token_out: spec.Address,
    *,
    fee: int,
    amount_in: int,
    sqrt_price_limit_x96: int = 0,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'quoteExactInputSingle',
        'quoter',
    )
    result = await rpc.async_eth_call(
        to_address=uniswap_v3_spec.quoter,
        function_abi=function_abi,
        function_parameters=[
            token_in,
            token_out,
            fee,
            amount_in,
            sqrt_price_limit_x96,
        ],
        provider=provider,
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_quote_exact_input(
    path: str,
    amount_in: int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'quoteExactInput',
        'quoter',
    )
    result = await rpc.async_eth_call(
        to_address=uniswap_v3_spec.quoter,
        function_abi=function_abi,
        function_parameters=[path, amount_in],
        provider=provider,
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_quote_exact_output_single(
    token_in: spec.Address,
    token_out: spec.Address,
    *,
    fee: int,
    amount_out: int,
    sqrt_price_limit_x96: int = 0,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'quoteExactOutputSingle',
        'quoter',
    )
    result = await rpc.async_eth_call(
        to_address=uniswap_v3_spec.quoter,
        function_abi=function_abi,
        function_parameters=[
            token_in,
            token_out,
            fee,
            amount_out,
            sqrt_price_limit_x96,
        ],
        provider=provider,
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_quote_exact_output(
    path: str,
    amount_in: int,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int:
    function_abi = await uniswap_v3_spec.async_get_function_abi(
        'quoteExactOutput',
        'quoter',
    )
    result = await rpc.async_eth_call(
        to_address=uniswap_v3_spec.quoter,
        function_abi=function_abi,
        function_parameters=[path, amount_in],
        provider=provider,
        block_number=block,
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result
