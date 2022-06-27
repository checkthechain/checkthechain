from __future__ import annotations

import typing

from ctc.toolbox import search_utils

from ctc import rpc
from ctc import spec
from .. import address_utils
from . import block_crud


async def async_get_contract_creation_block(
    contract_address: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    use_db: bool = True,
    **search_kwargs: typing.Any,
) -> int | None:
    """get block number of when contract was created

    - caches result in local database
    - behavior is undefined for functions that have undergone SELF-DESTRUCT(S)
    """

    network = rpc.get_provider_network(provider)

    if use_db:
        from ctc import db

        block = await db.async_query_contract_creation_block(
            address=contract_address,
            network=network,
        )
        if block is not None:
            return block

    block = await async_get_contract_creation_block_from_node(
        contract_address=contract_address,
        provider=provider,
        **search_kwargs,
    )

    if use_db and block is not None:
        await db.async_intake_contract_creation_block(
            contract_address=contract_address,
            block=block,
            network=network,
        )

    return block


async def async_get_contract_creation_block_from_node(
    contract_address: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
    verbose: bool = True,
    nary: typing.Optional[int] = None,
) -> int | None:
    """get the block where a contract was created

    algorithm: perform a binary search across blocks, check code bytes in each
    """

    contract_address = address_utils.get_address_checksum(contract_address)

    if start_block is None:
        start_block = 0
    if end_block is None:
        end_block = 'latest'
    if start_block == 'latest' or end_block == 'latest':
        latest_block = await block_crud.async_get_latest_block_number(
            provider=provider
        )
        if start_block == 'latest':
            start_block = latest_block
        if end_block == 'latest':
            end_block = latest_block

    if not isinstance(start_block, int):
        raise Exception('unknown start_block representation')
    if not isinstance(end_block, int):
        raise Exception('unknown end_block representation')

    if verbose:
        print('searching for creation block of ' + contract_address)

    async def async_is_match(index: int) -> bool:
        if verbose:
            print('- trying block:', index)
        return await address_utils.async_is_contract_address(
            address=contract_address,
            block=index,
            provider=provider,
        )

    if nary is None:
        result = await search_utils.async_binary_search(
            start_index=start_block,
            end_index=end_block,
            async_is_match=async_is_match,
        )
    else:
        raise NotImplementedError()

    if verbose:
        print('result:', result)

    return result
