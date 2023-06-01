from __future__ import annotations

import typing

from ctc import spec
from .. import abi_utils
from .. import address_utils
from .. import binary_utils
from . import erc20_generic
from . import erc20_spec


async def async_get_erc20_address(
    token: spec.ERC20Reference,
    *,
    context: spec.Context = None,
    case_insensitive_query: bool = True,
) -> spec.ERC20Address:
    """return address of input token, input as either symbol or address"""

    if isinstance(token, bytes):
        token = binary_utils.to_hex(token)

    if address_utils.is_address_str(token):
        return token
    elif isinstance(token, str):
        from ctc import db

        metadata = await db.async_query_erc20_metadata(
            symbol=token,
            context=context,
        )

        # if no result, try again case insensitive
        if metadata is None:
            metadata = await db.async_query_erc20_metadata(
                symbol=token,
                context=context,
                case_insensitive_symbol=case_insensitive_query,
            )

        if metadata is not None:
            address = metadata['address']
            if isinstance(address, str):
                return address

    raise Exception('could not get token address')


async def async_is_erc20(
    address_or_abi: spec.Address | spec.ContractABI,
    *,
    context: spec.Context = None,
) -> bool:
    """return whether an address implements ERC20 spec in its abi"""

    # get contract abi
    if address_utils.is_address_str(address_or_abi):
        contract_abi = await abi_utils.async_get_contract_abi(
            address_or_abi, context=context
        )
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


async def async_get_default_erc20_tokens(
    context: spec.Context = None,
) -> typing.Sequence[spec.ERC20Metadata]:
    """get list of default ERC20s

    TODO: add db table for tracking erc20 token lists
    - use a token list as tokens to check during block exploration
    - "default" can be one of the token lists
    """
    from ctc.config.setup_utils.default_data import default_erc20s

    return default_erc20s.load_default_erc20s(context=context)


async def async_get_erc20_metadata(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> spec.ERC20Metadata:
    """get metadata for ERC20 token"""

    address = await async_get_erc20_address(token, context=context)

    symbol_coroutine = async_get_erc20_symbol(
        token=token, block=block, context=context, **rpc_kwargs
    )
    decimals_coroutine = async_get_erc20_decimals(
        token=token, block=block, context=context, **rpc_kwargs
    )
    name_coroutine = async_get_erc20_name(
        token=token, block=block, context=context, **rpc_kwargs
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
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> int:
    """get decimals of an erc20"""

    from ctc import config

    result: spec.ERC20Metadata | None = None

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='erc20_metadata', context=context
    )

    if read_cache:
        from ctc import db

        token = await async_get_erc20_address(token, context=context)
        result = await db.async_query_erc20_metadata(
            address=token, context=context
        )
        if result is not None and result['decimals'] is not None:
            return result['decimals']

    decimals_result = await erc20_generic.async_erc20_eth_call(
        function_name='decimals',
        token=token,
        block=block,
        context=context,
        **rpc_kwargs,
    )
    if not isinstance(decimals_result, int) and not rpc_kwargs.get(
        'convert_reverts_to_none'
    ):
        raise Exception('invalid rpc result')
    decimals = decimals_result

    if write_cache:
        if result is not None:
            result['decimals'] = decimals
        else:
            data = {'address': token, 'decimals': decimals}
            if typing.TYPE_CHECKING:
                result = typing.cast(spec.ERC20Metadata, data)
            else:
                result = data
        await db.async_intake_erc20_metadata(context=context, **result)

    return decimals


async def async_get_erc20s_decimals(
    tokens: typing.Iterable[spec.ERC20Reference],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[int]:
    """get decimals of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='decimals',
        tokens=tokens,
        block=block,
        context=context,
        **rpc_kwargs,
    )


async def async_get_erc20_decimals_by_block(
    token: spec.ERC20Reference,
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[int]:
    """get decimals of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='decimals',
        token=token,
        blocks=blocks,
        context=context,
        **rpc_kwargs,
    )


#
# # name
#


@typing.overload
async def async_get_erc20_name(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    convert_reverts_to_none: typing.Literal[True],
    **rpc_kwargs: typing.Any,
) -> str | None:
    ...


@typing.overload
async def async_get_erc20_name(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    convert_reverts_to_none: typing.Literal[False] = False,
    **rpc_kwargs: typing.Any,
) -> str:
    ...


@typing.overload
async def async_get_erc20_name(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    convert_reverts_to_none: bool,
    **rpc_kwargs: typing.Any,
) -> str | None:
    ...


async def async_get_erc20_name(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    convert_reverts_to_none: bool = False,
    **rpc_kwargs: typing.Any,
) -> str | None:
    """get name of an erc20"""

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='erc20_metadata', context=context
    )

    result: spec.ERC20Metadata | None = None
    if read_cache:
        from ctc import db

        token = await async_get_erc20_address(token, context=context)
        result = await db.async_query_erc20_metadata(
            address=token, context=context
        )
        if result is not None and result['name'] is not None:
            return result['name']

    rpc_result: str | None = await erc20_generic.async_erc20_eth_call(
        function_name='name',
        token=token,
        block=block,
        context=context,
        **rpc_kwargs,
    )
    if not isinstance(rpc_result, str) and not convert_reverts_to_none:
        raise Exception('invalid rpc result')
    name = rpc_result

    if write_cache:
        if result is not None:
            result['name'] = name
        else:
            data = {'address': token, 'name': name}
            if typing.TYPE_CHECKING:
                result = typing.cast(spec.ERC20Metadata, data)
            else:
                result = data

        await db.async_intake_erc20_metadata(context=context, **result)

    return name


async def async_get_erc20s_names(
    tokens: typing.Iterable[spec.ERC20Reference],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[str]:
    """get name of multiple erc20s"""
    return await erc20_generic.async_erc20s_eth_calls(
        function_name='name',
        tokens=tokens,
        block=block,
        context=context,
        **rpc_kwargs,
    )


async def async_get_erc20_name_by_block(
    token: spec.ERC20Reference,
    *,
    blocks: typing.Iterable[spec.BlockNumberReference],
    context: spec.Context = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[str]:
    """get name of an erc20 across multiple blocks"""
    return await erc20_generic.async_erc20_eth_call_by_block(
        function_name='name',
        token=token,
        blocks=blocks,
        context=context,
        **rpc_kwargs,
    )


#
# # symbol
#


def _decode_raw_symbol(data: str | None, none_value: str | None = None) -> str:
    """special case decode of ancient non-compliant implementations of symbol"""

    if data is None:
        if none_value is None:
            none_value = ''
        return none_value
    elif len(data) == 66:
        return binary_utils.binary_to_text(data).strip('\x00')
    elif len(data) == 0 or data == '0x':
        return ''
    else:
        as_binary = binary_utils.to_binary(data)
        as_str: str = abi_utils.abi_decode(as_binary, '(string)')[0]
        return as_str


async def async_get_erc20_symbol(
    token: spec.ERC20Reference,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    convert_reverts_to: str | None = None,
    **rpc_kwargs: typing.Any,
) -> str:
    """get symbol of an erc20"""

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='erc20_metadata', context=context
    )

    if read_cache:
        from ctc import db

        token = await async_get_erc20_address(token, context=context)
        result: spec.ERC20Metadata | None = await db.async_query_erc20_metadata(
            address=token, context=context
        )
        if result is not None and result['symbol'] is not None:
            return result['symbol']

    symbol_raw = await erc20_generic.async_erc20_eth_call(
        function_name='symbol',
        token=token,
        block=block,
        decode_response=False,
        context=context,
        convert_reverts_to_none=(convert_reverts_to is not None),
        **rpc_kwargs,
    )
    symbol = _decode_raw_symbol(symbol_raw, none_value=convert_reverts_to)

    if write_cache:
        if result is not None:
            result['symbol'] = symbol
        else:
            data = {'address': token, 'symbol': symbol}
            if typing.TYPE_CHECKING:
                result = typing.cast(spec.ERC20Metadata, data)
            else:
                result = data

        await db.async_intake_erc20_metadata(context=context, **result)

    return symbol


async def async_get_erc20s_symbols(
    tokens: typing.Iterable[spec.ERC20Reference],
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    convert_reverts_to: str | None = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[str]:
    """get symbol of multiple erc20s"""
    results = await erc20_generic.async_erc20s_eth_calls(
        function_name='symbol',
        tokens=tokens,
        block=block,
        decode_response=False,
        context=context,
        convert_reverts_to_none=(convert_reverts_to is not None),
        **rpc_kwargs,
    )
    return [
        _decode_raw_symbol(result, none_value=convert_reverts_to)
        for result in results
    ]


async def async_get_erc20_symbol_by_block(
    token: spec.ERC20Reference,
    *,
    blocks: typing.Iterable[spec.BlockNumberReference],
    context: spec.Context = None,
    convert_reverts_to: str | None = None,
    **rpc_kwargs: typing.Any,
) -> typing.Sequence[str]:
    """get symbol of an erc20 across multiple blocks"""
    results = await erc20_generic.async_erc20_eth_call_by_block(
        function_name='symbol',
        token=token,
        blocks=blocks,
        decode_response=False,
        context=context,
        convert_reverts_to_none=(convert_reverts_to is not None),
        **rpc_kwargs,
    )
    return [
        _decode_raw_symbol(result, none_value=convert_reverts_to)
        for result in results
    ]

