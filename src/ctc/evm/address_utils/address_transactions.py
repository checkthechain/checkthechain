from __future__ import annotations

import typing

from ctc import evm
from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    class AddressTransactionCounts(TypedDict):
        blocks: list[int]
        diffs: list[int]
        cummulative: list[int]


@typing.overload
async def async_get_transactions_from_address(
    address: spec.Address,
    output_format: typing.Literal['dataframe'],
    *,
    context: spec.Context = None,
) -> spec.DataFrame:
    ...


@typing.overload
async def async_get_transactions_from_address(
    address: spec.Address,
    output_format: typing.Literal['hashes'],
    *,
    context: spec.Context = None,
) -> typing.Sequence[str]:
    ...


@typing.overload
async def async_get_transactions_from_address(
    address: spec.Address,
    output_format: typing.Literal['full'] = 'full',
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction]:
    ...


@typing.overload
async def async_get_transactions_from_address(
    address: spec.Address,
    output_format: typing.Literal['full', 'dataframe', 'hashes'],
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction] | spec.DataFrame | typing.Sequence[
    str
]:
    ...


async def async_get_transactions_from_address(
    address: spec.Address,
    output_format: typing.Literal['full', 'dataframe', 'hashes'] = 'full',
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.DBTransaction] | spec.DataFrame | typing.Sequence[
    str
]:
    """get all transactions from an address"""

    address = address.lower()

    count_data = await async_get_address_transaction_counts_by_block(
        address, context=context
    )

    # note: this can be made much more efficient with proper queries
    transactions = []
    for block_number, block_count in zip(
        count_data['blocks'],
        count_data['diffs'],
    ):
        block_transactions = await evm.async_get_block_transactions(
            block=block_number,
            context=context,
        )
        n_block_transactions = 0
        for transaction in block_transactions:
            if transaction['from_address'] == address:
                transactions.append(transaction)
                n_block_transactions += 1
                if n_block_transactions == block_count:
                    break
    if output_format == 'full':
        return transactions
    elif output_format == 'dataframe':
        import polars as pl

        return pl.DataFrame(transactions)
    elif output_format == 'hashes':
        return [transaction['hash'] for transaction in transactions]
    else:
        raise Exception('unknown output format: ' + str(output_format))


async def async_get_address_transaction_counts_by_block(
    address: spec.Address,
    nary: int = 3,
    *,
    context: spec.Context = None,
) -> AddressTransactionCounts:
    """return historical transaction count of address by block"""

    import asyncio
    from ctc import rpc

    address = address.lower()

    # get initial data
    min_block = 0
    min_count_coroutine = rpc.async_eth_get_transaction_count(
        from_address=address,
        block_number=0,
        context=context,
    )
    min_count_task = asyncio.create_task(min_count_coroutine)
    max_block = await rpc.async_eth_block_number(context=context)
    max_count = await rpc.async_eth_get_transaction_count(
        from_address=address,
        block_number=max_block,
        context=context,
    )
    min_count = await min_count_task

    block_counts = {
        min_block: min_count,
        max_block: max_count,
    }

    await _async_get_block_range_transaction_counts(
        address=address,
        min_block=min_block,
        max_block=max_block,
        block_counts=block_counts,
        nary=nary,
        context=context,
    )

    # parse blocks that contain transactions
    blocks = []
    diffs = []
    cummulative = []
    as_tuples = sorted(block_counts.items())
    for before, after in zip(as_tuples[:-1], as_tuples[1:]):
        if before[0] + 1 == after[0] and before[1] != after[1]:
            blocks.append(after[0])
            diffs.append(after[1] - before[1])
            cummulative.append(after[1])

    return {
        'blocks': blocks,
        'diffs': diffs,
        'cummulative': cummulative,
    }


async def _async_get_block_range_transaction_counts(
    *,
    address: spec.Address,
    min_block: int,
    max_block: int,
    block_counts: dict[int, int],
    nary: int,
    context: spec.Context = None,
) -> None:

    import asyncio
    import numpy as np
    from ctc import rpc

    n_unknown_blocks = max_block - min_block - 1
    if n_unknown_blocks <= 0:
        return

    blocks = np.linspace(
        min_block,
        max_block,
        min(nary + 1, n_unknown_blocks + 2),
    )[1:-1].astype(int)

    coroutines = [
        rpc.async_eth_get_transaction_count(
            from_address=address,
            block_number=block,
            context=context,
        )
        for block in blocks
    ]
    counts = await asyncio.gather(*coroutines)
    for block, count in zip(blocks, counts):
        block_counts[block] = count

    all_blocks = [min_block] + list(blocks) + [max_block]

    recursive_coroutines = []
    for range_min_block, range_max_block in zip(
        all_blocks[:-1], all_blocks[1:]
    ):
        range_min_count = block_counts[range_min_block]
        range_max_count = block_counts[range_max_block]

        if range_min_count == range_max_count:
            continue
        elif (
            range_min_count + 1 == range_max_count
            and range_min_block + 1 == range_max_block + 1
        ):
            continue
        else:
            coroutine = _async_get_block_range_transaction_counts(
                address=address,
                min_block=range_min_block,
                max_block=range_max_block,
                block_counts=block_counts,
                nary=nary,
                context=context,
            )
            recursive_coroutines.append(coroutine)
    await asyncio.gather(*recursive_coroutines)

