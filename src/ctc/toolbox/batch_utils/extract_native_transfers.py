from __future__ import annotations

import asyncio
import shutil
import typing

import polars as pl

import ctc.rpc
from . import block_chunk_jobs


class ExtractEthTransfers(block_chunk_jobs.BlockChunkJobs):
    def execute_job(self, i: int) -> typing.Any:
        job_data = self.get_job_data(i)
        job_name = self.get_job_name(i)
        path = self.get_job_output_path(i)
        sync_extract_eth_transfers(
            start_block=job_data['start_block'],
            end_block=job_data['end_block'],
            job_name=job_name,
            path=path,
        )


def sync_extract_eth_transfers(
    start_block: int, end_block: int, job_name: str, path: str
) -> None:
    try:
        asyncio.run(
            async_extract_native_transfers(start_block, end_block, path=path)
        )
    except Exception as e:
        print('job', job_name, 'failed:' + str(e))


async def async_extract_native_transfers(
    start_block: int, end_block: int, path: str
) -> None:

    transfers = ctc.async_trace_native_transfers(
        start_block=start_block,
        end_block=end_block,
    )

    await ctc.rpc.async_close_http_session()

    # load data into output file
    df = pl.DataFrame(
        transfers,
        orient="row",
        columns=[
            ('block_number', pl.datatypes.Int32),
            ('transfer_index', pl.datatypes.Int32),
            ('transaction_hash', pl.datatypes.Utf8),
            ('from_address', pl.datatypes.Utf8),
            ('to_address', pl.datatypes.Utf8),
            ('value', pl.datatypes.Utf8),
            ('error', pl.datatypes.Utf8),
        ],
    )
    temp_path = path + '_temp'
    df.write_parquet(temp_path)
    shutil.move(temp_path, path)




