from __future__ import annotations

import asyncio
import decimal
import os
import typing

import polars as pl

import ctc.rpc
from ctc import spec
from ctc.toolbox import pl_utils

try:
    import pdp
    import tooljob.trackers.multifile_tracker
except ImportError:
    raise Exception('install pdp for dataset functionality')


class ExtractBlocksAndTransactions(pdp.BlockChunkJobs):
    extract_blocks: bool
    extract_transactions: bool
    tracker: tooljob.trackers.multifile_tracker.MultifileTracker

    def __init__(
        self,
        extract_blocks: bool = True,
        extract_transactions: bool = True,
        **kwargs: typing.Any,
    ) -> None:
        self.extract_blocks = extract_blocks
        self.extract_transactions = extract_transactions
        super().__init__(outputs=['blocks', 'transactions'], **kwargs)

    def execute_job(self, i: int) -> typing.Any:
        job_data = self.get_job_data(i)
        job_name = self.get_job_name(i)
        paths = self.tracker.get_job_output_paths(i)
        sync_extract_blocks_and_transactions(
            start_block=job_data['start_block'],
            end_block=job_data['end_block'],
            job_name=job_name,
            paths=paths,
            context=self.context,
            extract_blocks=self.extract_blocks,
            extract_transactions=self.extract_transactions,
        )


def sync_extract_blocks_and_transactions(
    *,
    start_block: int,
    end_block: int,
    job_name: str,
    paths: typing.Mapping[str, str],
    context: spec.Context,
    extract_blocks: bool,
    extract_transactions: bool,
) -> None:
    try:
        coroutine = async_extract_blocks_and_transactions(
            start_block=start_block,
            end_block=end_block,
            paths=paths,
            context=context,
            extract_blocks=extract_blocks,
            extract_transactions=extract_transactions,
        )
        asyncio.run(coroutine)
    except Exception as e:
        print('job', job_name, 'failed:' + str(e))
        raise e


async def async_extract_blocks_and_transactions(
    *,
    start_block: int,
    end_block: int,
    paths: typing.Mapping[str, str],
    context: spec.Context,
    extract_blocks: bool,
    extract_transactions: bool,
) -> None:

    # get paths
    if all(os.path.isfile(path) for path in paths.values()):
        return

    extract_blocks &= not os.path.isfile(paths['blocks'])
    extract_transactions &= not os.path.isfile(paths['transactions'])

    # collect data
    coroutines = []
    for block_number in range(start_block, end_block + 1):
        coroutine = ctc.rpc.async_eth_get_block_by_number(
            block_number=block_number,
            context=context,
            include_full_transactions=extract_transactions,
        )
        coroutines.append(coroutine)
    raw_blocks = await asyncio.gather(*coroutines)
    await ctc.rpc.async_close_http_session(context=context)

    # extract blocks
    if extract_blocks:
        blocks_df = raw_blocks_to_dataframe(raw_blocks)
        pl_utils.write_df(df=blocks_df, path=paths['blocks'])

    # extract transactions
    if extract_transactions:
        transactions_df = raw_transactions_to_dataframe(raw_blocks)
        pl_utils.write_df(df=transactions_df, path=paths['transactions'])


def raw_blocks_to_dataframe(
    raw_blocks: typing.Sequence[typing.Mapping[str, typing.Any]]
) -> spec.DataFrame:
    # process raw blocks
    blocks = []
    for raw_block in raw_blocks:
        block = {
            'base_fee_per_gas': raw_block['base_fee_per_gas'],
            'gas_limit': raw_block['gas_limit'],
            'gas_used': raw_block['gas_used'],
            'hash': raw_block['hash'],
            'miner': raw_block['miner'],
            'block_number': raw_block['number'],
            'timestamp': raw_block['timestamp'],
        }
        blocks.append(block)

    # create dataframe
    blocks_schema = {
        'base_fee_per_gas': pl.UInt64,
        'gas_limit': pl.UInt32,
        'gas_used': pl.UInt32,
        'hash': pl.Utf8,
        'miner': pl.Utf8,
        'block_number': pl.UInt32,
        'timestamp': pl.UInt32,
    }
    blocks_df = pl.DataFrame(blocks, schema=blocks_schema)

    # convert binary fields
    binary_fields = [
        'hash',
        'miner',
    ]
    blocks_df = blocks_df.with_columns(
        blocks_df[binary_fields].select(
            pl.col('*').str.slice(2).str.decode('hex')
        )
    )

    return blocks_df


def raw_transactions_to_dataframe(
    raw_blocks: typing.Sequence[typing.Mapping[str, typing.Any]]
) -> spec.DataFrame:
    """
    Not currently included:
    - signature data: v, r, s
    - receipt data: gas_used, gas_price, status
    - access_list
    """

    # process raw transactions
    transactions = []
    for raw_block in raw_blocks:
        for raw_tx in raw_block['transactions']:
            to = raw_tx.get('to')
            if to is None:
                to = '0x0000000000000000000000000000000000000000'
            transaction = {
                'transaction_hash': raw_tx['hash'],
                'block_number': raw_tx['block_number'],
                'transaction_index': raw_tx['transaction_index'],
                'to_address': to,
                'from_address': raw_tx['from'],
                'value_float': float(raw_tx['value']),
                'value_decimal': decimal.Decimal(raw_tx['value']),
                'input': raw_tx['input'],
                'nonce': raw_tx['nonce'],
                'transaction_type': raw_tx['type'],
                'gas_limit': raw_tx['gas'],
                'gas_priority_max': raw_tx.get('max_priority_fee_per_gas'),
                'gas_price_max': raw_tx.get('max_fee_per_gas'),
                'gas_price': raw_tx.get('gas_price'),
            }
            transactions.append(transaction)

    # create dataframe
    transactions_schema = {
        'transaction_hash': pl.Utf8,
        'block_number': pl.UInt32,
        'transaction_index': pl.UInt32,
        'to_address': pl.Utf8,
        'from_address': pl.Utf8,
        'value_float': pl.Float64,
        'value_decimal': pl.Decimal,
        'input': pl.Utf8,
        'nonce': pl.UInt32,
        'transaction_type': pl.UInt8,
        'gas_limit': pl.Int64,
        'gas_priority_max': pl.Int64,
        'gas_price_max': pl.Int64,
        'gas_price': pl.Int64,
    }
    transactions_df = pl.DataFrame(transactions, schema=transactions_schema)

    # convert binary fields
    binary_fields = [
        'transaction_hash',
        'to_address',
        'from_address',
        'input',
    ]
    transactions_df = transactions_df.with_columns(
        transactions_df[binary_fields].select(
            pl.col('*').str.slice(2).str.decode('hex')
        )
    )

    return transactions_df

