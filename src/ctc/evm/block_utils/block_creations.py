from __future__ import annotations

import asyncio
import typing

from ctc.toolbox import search_utils

from ctc import rpc
from ctc import spec
from .. import address_utils
from . import block_crud


async def async_get_contract_creation_block(
    contract_address: spec.Address,
    provider: spec.ProviderSpec = None,
    **search_kwargs: typing.Any,
) -> int:

    network = rpc.get_provider_network(provider)

    # first check db
    use_db = True
    if use_db:
        block = await async_get_contract_creation_block_from_db(
            contract_address=contract_address,
            network=network,
        )
    else:
        block = None

    # if not in db, use rpc provider
    if block is None:
        latest_block_task = asyncio.create_task(
            block_crud.async_get_latest_block_number(provider=provider)
        )
        block = await async_get_contract_creation_block_from_node(
            contract_address=contract_address,
            provider=provider,
            **search_kwargs,
        )

        # decide whether to store in db
        from ctc import db

        min_confirmations = db.get_min_confirmations(
            network=network,
            datatype='contract_creation_blocks',
        )
        latest_block = await latest_block_task
        store_in_db = latest_block - block > min_confirmations
        if store_in_db:
            engine = db.create_engine(datatype='contract_creation_blocks')
            if engine is not None:
                with engine.begin() as conn:
                    db.set_contract_creation_block(
                        conn=conn,
                        block_number=block,
                        address=contract_address,
                        network=network,
                    )

    return block


async def async_get_contract_creation_block_from_db(
    contract_address: spec.Address,
    network: spec.NetworkReference,
) -> int | None:
    from ctc import db

    engine = db.create_engine(datatype='contract_creation_blocks')
    if engine is not None:
        with engine.connect() as conn:
            return db.get_contract_creation_block(
                conn=conn,
                address=contract_address,
                network=network,
            )
    else:
        return None


async def async_get_contract_creation_block_from_node(
    contract_address: spec.Address,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
    verbose: bool = True,
    nary: typing.Optional[int] = None,
) -> int:
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

