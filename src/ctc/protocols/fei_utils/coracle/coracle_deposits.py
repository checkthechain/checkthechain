import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from . import coracle_spec


#
# # multiple token information
#


async def async_get_tokens_in_pcv(
    block: spec.BlockReference = 'latest',
    wrapper: bool = False,
    provider: spec.ProviderSpec = None,
) -> list[spec.TokenAddress]:
    """get list of all tokens in pcv"""

    block = evm.standardize_block_number(block)
    coracle = coracle_spec.get_coracle_address(wrapper=wrapper, block=block)

    return await rpc.async_eth_call(
        to_address=coracle,
        function_name='getTokensInPcv',
        block_number=block,
        provider=provider,
    )


async def async_get_tokens_deposits(
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> dict[spec.TokenAddress, typing.Tuple[spec.ContractAddress, ...]]:
    """get all deposits of all tokens in pcv"""

    block = await evm.async_block_number_to_int(block=block, provider=provider)

    # get tokens in pcv
    tokens_in_pcv = await async_get_tokens_in_pcv(
        block=block, provider=provider
    )

    # get deposits of each token
    coroutines = []
    for token in tokens_in_pcv:
        coroutine = async_get_token_deposits(
            token=token,
            block=block,
            provider=provider,
        )
        coroutines.append(coroutine)

    # compile into tokens_deposits
    results = await asyncio.gather(*coroutines)
    tokens_deposits = dict(zip(tokens_in_pcv, results))
    return tokens_deposits


#
# # token deposit information
#


async def async_get_token_deposits(
    token: spec.TokenAddress,
    block: spec.BlockNumberReference = 'latest',
    wrapper: bool = False,
    provider: spec.ProviderSpec = None,
) -> typing.Tuple[spec.ContractAddress, ...]:
    """get list of a token's deposits"""

    block = evm.standardize_block_number(block)
    coracle = coracle_spec.get_coracle_address(wrapper=wrapper, block=block)
    return await rpc.async_eth_call(
        to_address=coracle,
        block_number=block,
        function_name='getDepositsForToken',
        function_parameters={'_token': token},
        provider=provider,
    )


async def async_get_pcv_token_balance(
    token: spec.TokenAddress,
    block: spec.BlockNumberReference = None,
    provider: spec.ProviderSpec = None,
):

    block = await evm.async_block_number_to_int(block, provider=provider)
    deposits = await async_get_token_deposits(token=token, block=block)

    coroutines = []
    for deposit in deposits:
        coroutine = async_get_deposit_token_balance(
            deposit_address=deposit,
            block=block,
            provider=provider,
        )
        coroutines.append(coroutine)

    deposit_balances = await asyncio.gather(*coroutines)

    return sum(deposit_balances)


#
# # deposit data
#


async def async_get_deposit_token_balance(
    deposit_address: spec.ContractAddress,
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> typing.Union[int, float]:
    """get token balance of a particular deposit"""

    block = evm.standardize_block_number(block)

    return await rpc.async_eth_call(
        to_address=deposit_address,
        function_name='balance',
        block_number=block,
        provider=provider,
    )


#
# # oracles
#


async def async_get_token_oracle(
    token: spec.TokenAddress,
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> spec.ContractAddress:

    block = evm.standardize_block_number(block)
    return await rpc.async_eth_call(
        to_address=coracle_spec.get_coracle_address(block=block),
        function_name='tokenToOracle',
        function_parameters=[token],
        block_number=block,
        provider=provider,
    )


async def async_get_token_price(
    token: spec.TokenAddress,
    block: typing.Optional[spec.BlockReference],
    blocks: typing.Optional[list[spec.BlockReference]] = None,
    provider: spec.ProviderSpec = None,
) -> typing.Union[int, float, list[int], list[float]]:
    if block is None and blocks is None:
        block = 'latest'

    if block is not None:
        pass
    elif block is not None:
        pass
    else:
        raise Exception()

