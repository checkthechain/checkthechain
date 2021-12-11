import asyncio
import typing

from ctc import evm
from ctc import rpc
from ctc import spec
from . import coracle_oracles
from . import coracle_deposits


#
# # deposit balance getters
#


async def async_get_deposit_balance(
    deposit: spec.ContractAddress,
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> typing.Union[int, list[int]]:
    """get token balance of a particular deposit"""
    return await rpc.async_eth_call(
        to_address=deposit,
        function_name='balance',
        block_number=block,
        provider=provider,
    )


async def async_get_deposits_balances(
    deposits: typing.Iterable[spec.ContractAddress],
    block: spec.BlockReference = 'latest',
    provider: spec.ProviderSpec = None,
) -> list[int]:
    return await rpc.async_batch_eth_call(
        to_addresses=deposits,
        function_name='balance',
        block_number=block,
        provider=provider,
    )


async def async_get_deposit_balance_by_block(
    deposit: spec.ContractAddress,
    blocks: typing.Iterable[spec.BlockReference],
    provider: spec.ProviderSpec = None,
) -> list[int]:
    return await rpc.async_batch_eth_call(
        to_address=deposit,
        function_name='balance',
        block_numbers=blocks,
        provider=provider,
    )


#
# # token balance getters
#


async def async_get_token_balance(
    token: spec.TokenAddress,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    usd: bool = False,
) -> typing.Union[int, float]:

    block = await evm.async_block_number_to_int(block=block, provider=provider)
    deposits = await coracle_deposits.async_get_token_deposits(
        token=token, block=block, provider=provider
    )
    balances = await async_get_deposits_balances(
        deposits=deposits, block=block, provider=provider
    )
    balance: typing.Union[int, float] = sum(balances)

    if normalize:
        balance = await evm.async_normalize_erc20_quantity(
            quantity=balance,
            provider=provider,
            token=token,
        )

    if usd:
        if not normalize:
            raise Exception('must normalize for usd conversion')
        token_price = await coracle_oracles.async_get_token_price(
            token=token,
            block=block,
            provider=provider,
            normalize=True,
        )
        balance = balance * token_price

    return balance


async def async_get_token_balance_by_block(
    token: spec.TokenAddress,
    blocks: spec.BlockNumberReference,
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    usd: bool = False,
) -> typing.Union[list[int], list[float]]:

    blocks = await evm.async_block_numbers_to_int(blocks)
    blocks_deposits = await coracle_deposits.async_get_token_deposits(
        token=token, blocks=blocks, provider=provider
    )
    coroutines = []
    for block, block_deposits in zip(blocks, blocks_deposits):
        coroutine = async_get_deposits_balances(
            deposits=block_deposits,
            provider=provider,
            block=block,
        )
        coroutines.append(coroutine)
    blocks_balances = asyncio.gather(*coroutines)

    token_balances = [sum(block_balance) for block_balance in blocks_balances]

    if normalize:
        token_balances = await evm.async_normalize_erc20_quantity(
            quantities=token_balances,
            provider=provider,
            token=token,
        )

    if usd:
        if not normalize:
            raise Exception('must normalize for usd conversion')
        token_prices = await coracle_oracles.async_get_token_price(
            token=token,
            blocks=blocks,
            provider=provider,
            normalize=True,
        )
        token_balances = [
            token_balance * token_price
            for token_balance, token_price in zip(token_balances, token_prices)
        ]

    return token_balances


async def async_get_tokens_balances(
    tokens: spec.TokenAddress = None,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    usd: bool = False,
) -> typing.Union[dict[spec.TokenAddress, int], dict[spec.TokenAddress, float]]:

    block = await evm.async_block_number_to_int(block=block, provider=provider)

    if tokens is None:
        tokens = coracle_deposits.async_get_tokens_in_pcv(
            block=block, provider=provider
        )

    tokens_deposits = await coracle_deposits.async_get_tokens_deposits(
        tokens=tokens, block=block, provider=provider
    )
    all_deposits = [
        deposit
        for token_deposits in tokens_deposits.values()
        for deposit in token_deposits
    ]
    all_balances = await coracle_deposits.async_get_deposits_balances(
        deposits=all_deposits,
        provider=provider,
        block=block,
    )
    all_balances_iter = iter(all_balances)
    deposits_balances = {}
    for token, token_deposits in tokens_deposits.items():
        deposits_balances[token] = []
        for _ in token_deposits:
            deposits_balances[token].append(next(all_balances_iter))

    tokens_balances = {
        token: sum(token_balances)
        for token, token_balances in deposits_balances.items()
    }

    if normalize:
        normalized = await evm.async_normalize_erc20_quantity(
            quantities=tokens_balances.values(),
            tokens=tokens,
            block=block,
            provider=provider,
        )
        tokens_balances = dict(zip(tokens_balances.keys(), normalized))

    if usd:
        if not normalize:
            raise Exception('must normalize for usd conversion')
        token_prices = await coracle_oracles.async_get_token_price(
            tokens=tokens,
            block=block,
            provider=provider,
            normalize=True,
        )
        tokens_balances = {
            token: tokens_balances[token] * token_price
            for token, token_price in zip(tokens_balances, token_prices)
        }

    return tokens_balances


async def async_get_tokens_balances_by_block(
    blocks: spec.BlockNumberReference,
    tokens: spec.TokenAddress = None,
    provider: spec.ProviderSpec = None,
    normalize: bool = True,
    usd: bool = False,
) -> typing.Union[
    dict[spec.TokenAddress, list[int]],
    dict[spec.TokenAddress, list[float]],
]:

    # query data
    coroutines = []
    for block in blocks:
        coroutine = async_get_tokens_balances(
            tokens=tokens,
            block=block,
            provider=provider,
        )
        coroutines.append(coroutine)
    results = await asyncio.gather(*coroutines)

    # get list of all tokens
    all_tokens = []
    for result in results:
        for token in result.keys():
            all_tokens.append(token)
    all_tokens = list(set(all_tokens))

    # combine results into dict of lists
    tokens_balances = {token: [] for token in all_tokens}
    for result in results:
        for token in all_tokens:
            balance = result.get(token, 0)
            tokens_balances[token].append(balance)

    # normalize
    if normalize:
        coroutines = []
        for token, token_balances in tokens_balances.items():
            coroutine = evm.async_normalize_erc20_quantities(
                token=token, quantities=token_balances, provider=provider,
            )
            coroutines.append(coroutine)
        normalized = await asyncio.gather(*coroutines)
        tokens_balances = dict(zip(all_tokens, normalized))

    if usd:
        if not normalize:
            raise Exception('must normalize for usd conversion')

        blocks_tokens = []
        coroutines = []
        for block, result in zip(blocks, results):
            block_tokens = list(result.keys())
            blocks_tokens.append(block_tokens)
            coroutine = coracle_oracles.async_get_tokens_prices(
                tokens=block_tokens,
                block=block,
                provider=provider,
                normalize=True,
            )
            coroutines.append(coroutine)
        tokens_prices_per_block = await asyncio.gather(*coroutines)
        for b, block_tokens in enumerate(blocks_tokens):
            for t, token in enumerate(blocks_tokens):
                tokens_balances[token][b] *= tokens_prices_per_block[t]

    return tokens_balances

