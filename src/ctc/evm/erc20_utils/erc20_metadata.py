from __future__ import annotations

import typing

from ctc import config
from ctc import spec
from .. import abi_utils
from .. import address_utils
from .. import binary_utils
from . import erc20_generic
from . import erc20_spec


async def async_get_erc20_address(
    token: spec.ERC20Reference,
    network: spec.NetworkReference | None = None,
    *,
    case_insensitive_query: bool = True,
) -> spec.ERC20Address:
    """return address of input token, input as either symbol or address"""

    if address_utils.is_address_str(token):
        return token
    elif isinstance(token, str):
        from ctc import db

        if network is None:
            network = config.get_default_network()

        metadata = await db.async_query_erc20_metadata(
            symbol=token,
            network=network,
        )

        # if no result, try again case insensitive
        if metadata is None:
            metadata = await db.async_query_erc20_metadata(
                symbol=token,
                network=network,
                case_insensitive_symbol=case_insensitive_query,
            )

        if metadata is not None:
            address = metadata['address']
            if isinstance(address, str):
                return address

    raise Exception('could not get token address')


async def async_is_erc20(
    address_or_abi: spec.Address | spec.ContractABI,
) -> bool:
    """return whether an address implements ERC20 spec in its abi"""

    # get contract abi
    if address_utils.is_address_str(address_or_abi):
        contract_abi = await abi_utils.async_get_contract_abi(address_or_abi)
    elif isinstance(address_or_abi, list):
        contract_abi = address_or_abi
    contract_abi_by_selectors = abi_utils.get_contract_abi_by_selectors(
        contract_abi
    )

    # get erc20 abi
    erc20_abi: spec.ContractABI = list(erc20_spec.erc20_function_abis.values())
    erc20_abi += list(erc20_spec.erc20_event_abis.values())
    erc20_abi_by_selectors = abi_utils.get_contract_abi_by_selectors(erc20_abi)

    # compare abis
    for selector in erc20_abi_by_selectors.keys():
        if selector not in contract_abi_by_selectors:
            return False
    return True


async def async_get_default_erc20_tokens() -> typing.Sequence[
    spec.ERC20Metadata
]:
    """get list of default ERC20s

    TODO: add db table for tracking erc20 token lists
    - use a token list as tokens to check during block exploration
    - "default" can be one of the token lists
    """
    from ctc.config.setup_utils.default_data import default_erc20s

    return default_erc20s.load_default_erc20s()


async def async_get_erc20_metadata(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
    **rpc_kwargs: typing.Any,
) -> spec.ERC20Metadata:
    """get metadata for ERC20 token"""

    from ctc import rpc

    network = rpc.get_provider_network(provider)
    address = await async_get_erc20_address(token, network=network)

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
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    use_db: bool = True,
    provider: spec.ProviderReference = None,
    **rpc_kwargs: typing.Any,
) -> int:
    """get decimals of an erc20"""

    result: spec.ERC20Metadata | None = None

    if use_db:
        from ctc import db
        from ctc import rpc

        network = rpc.get_provider_network(provider)
        token = await async_get_erc20_address(token, network=network)
        result = await db.async_query_erc20_metadata(
            address=token, network=network
        )
        if result is not None and result['decimals'] is not None:
            return result['decimals']

    decimals_result = await erc20_generic.async_erc20_eth_call(
        function_name='decimals',
        token=token,
        block=block,
        provider=provider,
        **rpc_kwargs,
    )
    if not isinstance(decimals_result, int):
        raise Exception('invalid rpc result')
    decimals = decimals_result

    if use_db:
        if result is not None:
            result['decimals'] = decimals
        else:
            data = {'address': token, 'decimals': decimals}
            if typing.TYPE_CHECKING:
                result = typing.cast(spec.ERC20Metadata, data)
            else:
                result = data
        await db.async_intake_erc20_metadata(network=network, **result)

    return decimals


async def async_get_erc20s_decimals(
    tokens: typing.Iterable[spec.ERC20Reference],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    **rpc_kwargs: typing.Any,
) -> list[int]:
    """get decimals of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='decimals', tokens=tokens, block=block, **rpc_kwargs
    )


async def async_get_erc20_decimals_by_block(
    token: spec.ERC20Reference,
    *,
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
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    use_db: bool = True,
    provider: spec.ProviderReference = None,
    **rpc_kwargs: typing.Any,
) -> str:
    """get name of an erc20"""

    result: spec.ERC20Metadata | None = None
    if use_db:
        from ctc import db
        from ctc import rpc

        network = rpc.get_provider_network(provider)
        token = await async_get_erc20_address(token, network=network)
        result = await db.async_query_erc20_metadata(
            address=token, network=network
        )
        if result is not None and result['name'] is not None:
            return result['name']

    rpc_result = await erc20_generic.async_erc20_eth_call(
        function_name='name',
        token=token,
        block=block,
        provider=provider,
        **rpc_kwargs,
    )
    if not isinstance(rpc_result, str):
        raise Exception('invalid rpc result')
    name = rpc_result

    if use_db:
        if result is not None:
            result['name'] = name
        else:
            data = {'address': token, 'name': name}
            if typing.TYPE_CHECKING:
                result = typing.cast(spec.ERC20Metadata, data)
            else:
                result = data

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


def _decode_raw_symbol(data: str | None) -> str:
    """special case decode of ancient non-compliant implementations of symbol"""
    if data is None:
        return ''
    elif len(data) == 66:
        return binary_utils.binary_to_text(data).strip('\x00')
    elif len(data) == 0 or data == '0x':
        return ''
    else:
        as_binary = binary_utils.binary_convert(data, 'binary')
        as_str: str = abi_utils.abi_decode(as_binary, '(string)')[0]
        return as_str


async def async_get_erc20_symbol(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    use_db: bool = True,
    provider: spec.ProviderReference = None,
    **rpc_kwargs: typing.Any,
) -> str:
    """get symbol of an erc20"""

    if use_db:
        from ctc import db
        from ctc import rpc

        network = rpc.get_provider_network(provider)
        token = await async_get_erc20_address(token, network=network)
        result: spec.ERC20Metadata | None = await db.async_query_erc20_metadata(
            address=token, network=network
        )
        if result is not None and result['symbol'] is not None:
            return result['symbol']

    symbol_raw = await erc20_generic.async_erc20_eth_call(
        function_name='symbol',
        token=token,
        block=block,
        decode_response=False,
        provider=provider,
        **rpc_kwargs,
    )
    symbol = _decode_raw_symbol(symbol_raw)

    if use_db:
        if result is not None:
            result['symbol'] = symbol
        else:
            data = {'address': token, 'symbol': symbol}
            if typing.TYPE_CHECKING:
                result = typing.cast(spec.ERC20Metadata, data)
            else:
                result = data

        await db.async_intake_erc20_metadata(network=network, **result)

    return symbol


async def async_get_erc20s_symbols(
    tokens: typing.Iterable[spec.ERC20Reference],
    *,
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
    *,
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
