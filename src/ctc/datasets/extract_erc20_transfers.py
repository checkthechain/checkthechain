from __future__ import annotations

import asyncio
import typing
import shutil

import ctc.rpc
from ctc import spec
import tooljob

try:
    import pdp
except ImportError:
    raise Exception('install pdp for dataset functionality')


class ExtractErc20Transfers(pdp.BlockChunkJobs):
    tracker: tooljob.trackers.file_tracker.FileTracker

    def execute_job(self, i: int) -> typing.Any:
        job_data = self.get_job_data(i)
        job_name = self.get_job_name(i)
        path = self.tracker.get_job_output_path(i)
        sync_extract_erc20_transfers(
            start_block=job_data['start_block'],
            end_block=job_data['end_block'],
            job_name=job_name,
            path=path,
            context=self.context,
        )


def sync_extract_erc20_transfers(
    *,
    start_block: int,
    end_block: int,
    job_name: str,
    path: str,
    context: spec.Context,
) -> None:
    try:
        asyncio.run(
            async_extract_erc20_transfers(
                start_block=start_block,
                end_block=end_block,
                path=path,
                context=context,
            )
        )
    except Exception as e:
        print('job', job_name, 'failed:' + str(e))
        raise e


async def async_extract_erc20_transfers(
    *,
    start_block: int,
    end_block: int,
    path: str,
    context: spec.Context,
) -> None:

    event_hash = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
    encoded_transfers = await ctc.async_get_events(
        event_hash=event_hash,
        start_block=start_block,
        end_block=end_block,
        decode=False,
        context={'cache': False},
        verbose=False,
        max_blocks_per_request=100,
    )

    await ctc.rpc.async_close_http_session(context=context)

    # load data into output file
    decoded_transfers = (
        ctc.evm.erc20_utils.erc20_events._decode_erc20_transfers(
            encoded_transfers
        )
    )
    del encoded_transfers

    # write file
    temp_path = path + '_temp'
    if len(decoded_transfers) == 0:
        decoded_transfers.write_parquet(temp_path)
    else:
        decoded_transfers.write_parquet(
            temp_path,
            statistics=True,
            row_group_size=max(1000, int(len(decoded_transfers) / 64)),
        )
    shutil.move(temp_path, path)

