from __future__ import annotations

import typing

from ctc import binary
from ctc import rpc
from ctc import spec
from . import erc20_generic


async def async_get_erc20_metadata(
    token: spec.ERC20Reference,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs: typing.Any,
) -> spec.ERC20Metadata:

    network = rpc.get_provider_network(provider)
    address = await erc20_generic.async_get_erc20_address(
        token, network=network
    )

    symbol_coroutine = async_get_erc20_symbol(
        token=token, block=block, provider=provider, **rpc_kwargs
    )
    decimals_coroutine = async_get_erc20_decimals(
        token=token, block=block, provider=provider, **rpc_kwargs
    )
    name_coroutine = async_get_erc20_name(
        token=token, block=block, provider=provider, **rpc_kwargs
    )

    import asyncio

    symbol, decimals, name = await asyncio.gather(
        symbol_coroutine,
        decimals_coroutine,
        name_coroutine,
    )

    return {
        'address': address,
        'symbol': symbol,
        'decimals': decimals,
        'name': name,
    }


#
# # decimals
#


async def async_get_erc20_decimals(
    token: spec.ERC20Reference,
    block: typing.Optional[spec.BlockNumberReference] = None,
    use_db: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs: typing.Any,
) -> int:
    """get decimals of an erc20"""

    if use_db:
        from ctc import db

        network = rpc.get_provider_network(provider)
        token = await erc20_generic.async_get_erc20_address(
            token, network=network
        )
        result: spec.ERC20Metadata | None = (
            await db.async_query_erc20_metadata(address=token, network=network)
        )
        if result is not None and result['decimals'] is not None:
            return result['decimals']

    decimals = await erc20_generic.async_erc20_eth_call(
        function_name='decimals',
        token=token,
        block=block,
        provider=provider,
        **rpc_kwargs,
    )

    if use_db:
        if result is not None:
            result['decimals'] = decimals
        else:
            result = typing.cast(
                spec.ERC20Metadata,
                {
                    'address': token,
                    'decimals': decimals,
                }
            )
        await db.async_intake_erc20_metadata(network=network, **result)

    return decimals


async def async_get_erc20s_decimals(
    tokens: typing.Iterable[spec.ERC20Reference],
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> list[int]:
    """get decimals of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='decimals', tokens=tokens, block=block, **rpc_kwargs
    )


async def async_get_erc20_decimals_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Sequence[spec.BlockNumberReference],
    **rpc_kwargs: typing.Any,
) -> list[int]:
    """get decimals of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='decimals',
        token=token,
        blocks=blocks,
        **rpc_kwargs,
    )


#
# # name
#


async def async_get_erc20_name(
    token: spec.ERC20Reference,
    block: typing.Optional[spec.BlockNumberReference] = None,
    use_db: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs: typing.Any,
) -> str:
    """get name of an erc20"""

    if use_db:
        from ctc import db

        network = rpc.get_provider_network(provider)
        token = await erc20_generic.async_get_erc20_address(
            token, network=network
        )
        result: spec.ERC20Metadata | None = await db.async_query_erc20_metadata(
            address=token, network=network
        )
        if result is not None and result['name'] is not None:
            return result['name']

    name = await erc20_generic.async_erc20_eth_call(
        function_name='name',
        token=token,
        block=block,
        provider=provider,
        **rpc_kwargs,
    )

    if use_db:
        if result is not None:
            result['name'] = name
        else:
            result = typing.cast(
                spec.ERC20Metadata,
                {'address': token, 'name': name},
            )
        await db.async_intake_erc20_metadata(network=network, **result)

    return name


async def async_get_erc20s_names(
    tokens: typing.Iterable[spec.ERC20Reference],
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> list[str]:
    """get name of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='name', tokens=tokens, block=block, **rpc_kwargs
    )


async def async_get_erc20_name_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs: typing.Any,
) -> list[str]:
    """get name of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='name', token=token, blocks=blocks, **rpc_kwargs
    )


#
# # symbol
#


def _decode_raw_symbol(data: str) -> str:
    """special case decode of ancient non-compliant implementations of symbol"""
    if len(data) == 66:
        return binary.hex_to_ascii(data).strip('\x00')
    else:
        as_binary = binary.convert(data, 'binary')
        return binary.decode_types(as_binary, '(string)')[0]


async def async_get_erc20_symbol(
    token: spec.ERC20Reference,
    block: typing.Optional[spec.BlockNumberReference] = None,
    use_db: bool = True,
    provider: spec.ProviderSpec = None,
    **rpc_kwargs: typing.Any,
) -> str:
    """get symbol of an erc20"""

    if use_db:
        from ctc import db

        network = rpc.get_provider_network(provider)
        token = await erc20_generic.async_get_erc20_address(
            token, network=network
        )
        result: spec.ERC20Metadata | None = await db.async_query_erc20_metadata(
            address=token, network=network
        )
        if result is not None and result['symbol'] is not None:
            return result['symbol']

    symbol = await erc20_generic.async_erc20_eth_call(
        function_name='symbol',
        token=token,
        block=block,
        decode_response=False,
        provider=provider,
        **rpc_kwargs,
    )
    symbol = _decode_raw_symbol(symbol)

    if use_db:
        if result is not None:
            result['symbol'] = symbol
        else:
            result = typing.cast(
                spec.ERC20Metadata,
                {'address': token, 'symbol': symbol},
            )
        await db.async_intake_erc20_metadata(network=network, **result)

    return symbol


async def async_get_erc20s_symbols(
    tokens: typing.Iterable[spec.ERC20Reference],
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> list[str]:
    """get symbol of multiple erc20s"""
    results = await erc20_generic.async_erc20s_eth_calls(
        function_name='symbol',
        tokens=tokens,
        block=block,
        decode_response=False,
        **rpc_kwargs,
    )
    return [_decode_raw_symbol(result) for result in results]


async def async_get_erc20_symbol_by_block(
    token: spec.ERC20Reference,
    blocks: typing.Iterable[spec.BlockNumberReference],
    **rpc_kwargs: typing.Any,
) -> list[str]:
    """get symbol of an erc20 across multiple blocks"""
    results = await erc20_generic.async_erc20_eth_call_by_block(
        function_name='symbol',
        token=token,
        blocks=blocks,
        decode_response=False,
        **rpc_kwargs,
    )
    return [_decode_raw_symbol(result) for result in results]
