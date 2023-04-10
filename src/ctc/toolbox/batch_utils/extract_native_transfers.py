from __future__ import annotations

import asyncio
import shutil
import typing

import polars as pl

import ctc.rpc
from ctc import spec
from . import block_chunk_jobs


class ExtractNativeTransfers(block_chunk_jobs.BlockChunkJobs):
    def execute_job(self, i: int) -> typing.Any:
        job_data = self.get_job_data(i)
        job_name = self.get_job_name(i)
        path = self.tracker.get_job_output_path(i)
        sync_extract_native_transfers(
            start_block=job_data['start_block'],
            end_block=job_data['end_block'],
            job_name=job_name,
            path=path,
            context=self.context,
        )


def sync_extract_native_transfers(
    start_block: int,
    end_block: int,
    job_name: str,
    path: str,
    context: spec.Context,
) -> None:
    try:
        asyncio.run(
            async_extract_native_transfers(
                start_block,
                end_block,
                path=path,
                context=context,
            )
        )
    except Exception as e:
        print('job', job_name, 'failed:' + str(e))
        raise e


async def async_extract_native_transfers(
    start_block: int,
    end_block: int,
    path: str,
    context: spec.Context,
) -> None:

    transfers = await ctc.async_trace_native_transfers(
        start_block=start_block,
        end_block=end_block,
        context=context,
    )

    await ctc.rpc.async_close_http_session(context=context)

    # load data into output file
    df = pl.DataFrame(
        transfers,
        orient='row',
        schema=[
            ('block_number', pl.datatypes.Int32),
            ('transfer_index', pl.datatypes.Int32),
            ('transaction_hash', pl.datatypes.Utf8),
            ('from_address', pl.datatypes.Utf8),
            ('to_address', pl.datatypes.Utf8),
            ('value', pl.datatypes.Utf8),
        ],
    )
    temp_path = path + '_temp'
    df.write_csv(temp_path)
    shutil.move(temp_path, path)

