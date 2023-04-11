"""should move this file to evm.contract_utils"""

from __future__ import annotations

import typing

from ctc import spec
from .. import binary_utils
from .. import block_utils
from .. import transaction_utils
from . import contract_tests


def get_created_address(
    sender: spec.Address,
    nonce: int | None = None,
    *,
    salt: str | None = None,
    init_code: spec.HexData | None = None,
) -> spec.Address:
    """return address created by EVM opcodes CREATE or CREATE2

    see https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1014.md
    see https://ethereum.stackexchange.com/a/761
    """

    if nonce is not None:
        # create
        data: str | bytes = binary_utils.rlp_encode(
            (sender, nonce), str_mode='hex'
        )
    elif salt is not None and init_code is not None:
        # create2
        data = (
            binary_utils.to_hex('0xff', prefix=False)
            + binary_utils.to_hex(sender, prefix=False)
            + binary_utils.to_hex(salt, prefix=False)
            + binary_utils.to_hex(binary_utils.keccak(init_code), prefix=False)
        )
    else:
        raise Exception('specify either {nonce} or {salt, init_code}')

    result = binary_utils.keccak(data, output_format='prefix_hex')
    result = '0x' + result[26:]

    return result


async def async_get_contract_creation_transaction(
    contract_address: spec.Address,
    *,
    context: spec.Context = None,
    creation_block: int | None = None,
) -> spec.TransactionHash:
    """get hash of contract's creation transaction"""
    from ctc import rpc

    contract_address = contract_address.lower()

    if creation_block is None:
        creation_block = await async_get_contract_creation_block(
            contract_address, context=context
        )
    if creation_block is None:
        raise Exception('could not determine creation block of contract')
    trace_block: spec.TraceList = await rpc.async_trace_block(
        creation_block, context=context
    )
    for item in trace_block:
        if (
            item['type'] == 'create'
            and item['result']['address'] == contract_address  # type: ignore
        ):
            return item['transaction_hash']
    else:
        raise Exception('could not find creation transaction for contract')


async def async_get_contract_deployer(
    contract_address: spec.Address,
    *,
    creation_transaction: spec.TransactionHash | None = None,
    context: spec.Context = None,
) -> spec.Address:
    """get EOA deployer of contract"""
    if creation_transaction is None:
        creation_transaction = await async_get_contract_creation_transaction(
            contract_address, context=context
        )
    tx = await transaction_utils.async_get_transaction(
        creation_transaction, context=context
    )
    return tx['from_address']


async def async_get_contract_creation_block(
    contract_address: spec.Address,
    *,
    context: spec.Context = None,
    **search_kwargs: typing.Any,
) -> int | None:
    """get block number of when contract was created

    - behavior is undefined for functions that have undergone SELF-DESTRUCT(S)
    - caches result in local database
    """

    from ctc import config

    read_cache, write_cache = config.get_context_cache_read_write(
        schema_name='contract_creation_blocks', context=context
    )
    if read_cache:
        from ctc import db

        block = await db.async_query_contract_creation_block(
            address=contract_address,
            context=context,
        )
        if block is not None:
            return block

    block = await _async_get_contract_creation_block_from_node(
        contract_address=contract_address,
        context=context,
        **search_kwargs,
    )

    if write_cache and block is not None:
        await db.async_intake_contract_creation_block(
            contract_address=contract_address,
            block=block,
            context=context,
        )

    return block


async def async_get_contracts_creation_blocks(
    contract_addresses: typing.Sequence[spec.Address],
    *,
    verbose: bool = False,
    context: spec.Context = None,
    **search_kwargs: typing.Any,
) -> typing.Sequence[int | None]:
    """get creation blocks of mutliple contracts

    - behavior is undefined for functions that have undergone SELF-DESTRUCT(S)
    - caches results in local database
    """

    import asyncio

    coroutines = [
        async_get_contract_creation_block(
            contract_address=contract_address,
            context=context,
            verbose=verbose,
            **search_kwargs,
        )
        for contract_address in contract_addresses
    ]
    return await asyncio.gather(*coroutines)


async def _async_get_contract_creation_block_from_node(
    contract_address: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    context: spec.Context = None,
    verbose: bool = True,
    nary: typing.Optional[int] = None,
) -> int | None:
    """get the block where a contract was created

    algorithm: perform a binary search across blocks, check code bytes in each
    """

    from ctc.toolbox import search_utils

    if start_block is None:
        start_block = 0
    if end_block is None:
        end_block = 'latest'
    if start_block == 'latest' or end_block == 'latest':
        latest_block = await block_utils.async_get_latest_block_number(
            context=context
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
        return await contract_tests.async_is_contract_address(
            address=contract_address,
            block=index,
            context=context,
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

