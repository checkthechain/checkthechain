from __future__ import annotations

import asyncio
import os
import shutil
import typing

import polars as pl

import ctc
import ctc.rpc
from ctc import spec
from . import block_chunk_jobs


class ExtractCreateTraces(block_chunk_jobs.BlockChunkJobs):
    def execute_job(self, i: int) -> typing.Any:
        job_data = self.get_job_data(i)
        job_name = self.get_job_name(i)
        path = self.tracker.get_job_output_path(i)
        sync_trace_blocks(
            start_block=job_data['start_block'],
            end_block=job_data['end_block'],
            job_name=job_name,
            path=path,
            context=self.context,
        )


async def async_trace_blocks(
    *,
    start_block: int,
    end_block: int,
    path: str,
    context: spec.Context,
) -> None:
    create_traces = await ctc.async_trace_contract_creations(
        start_block=start_block,
        end_block=end_block,
        context=context,
    )
    await ctc.rpc.async_close_http_session()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    temp_path = path + '_temp'
    pl.DataFrame(create_traces).write_csv(temp_path)
    shutil.move(temp_path, path)

    return None


def sync_trace_blocks(
    *,
    start_block: int,
    end_block: int,
    job_name: str,
    path: str,
    context: spec.Context,
) -> None:
    try:
        asyncio.run(
            async_trace_blocks(
                start_block=start_block,
                end_block=end_block,
                path=path,
                context=context,
            )
        )
    except Exception as e:
        print('job', job_name, 'failed:' + str(e))

