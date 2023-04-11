from __future__ import annotations

import math
import typing

import polars as pl
import toolstr
import tooljob

from ctc import spec


class BlockChunkJobs(tooljob.Batch):
    """create jobs by splitting a block interval into chunks, one job for each chunk"""

    start_block: int
    end_block: int
    chunk_size: int
    context: spec.Context | None = None
    tracker: tooljob.trackers.file_tracker.FileTracker

    def __init__(
        self,
        start_block: int,
        end_block: int,
        chunk_size: int,
        context: spec.Context | None = None,
        **kwargs: typing.Any,
    ) -> None:
        if end_block < start_block:
            raise Exception('start_block must be less than end_block')
        self.start_block = start_block
        self.end_block = end_block
        self.chunk_size = chunk_size
        self.context = context
        super().__init__(**kwargs)

    #
    # # jobs
    #

    def get_n_jobs(self) -> int:
        n_blocks = self.end_block - self.start_block + 1
        return math.floor(n_blocks / self.chunk_size)

    def get_job_data(self, i: int) -> tooljob.JobData:
        n_jobs = self.get_n_jobs()
        if i < 0 or i >= n_jobs:
            raise Exception('job index too high, max is ' + str(n_jobs - 1))

        start_block = i * self.chunk_size + self.start_block
        end_block = (i + 1) * self.chunk_size - 1 + self.start_block
        if end_block > self.end_block:
            end_block = self.end_block

        return {'start_block': start_block, 'end_block': end_block}

    #
    # # names
    #

    def get_job_name(
        self,
        i: int | None = None,
        *,
        job_data: tooljob.JobData | None = None,
    ) -> str:
        if job_data is None:
            if i is None:
                raise Exception('must specify job_data or i')
            job_data = self.get_job_data(i)
        return self.get_job_list_name() + '__' + self.get_block_range_str(i)

    def parse_job_name(self, name: str) -> typing.Mapping[str, typing.Any]:
        block_range = name.split('__')[-1]
        start_str, end_str = block_range.split('_to_')
        return {'start_block': int(start_str), 'end_block': int(end_str)}

    def get_block_range_str(
        self,
        i: int | None = None,
        *,
        start_block: int | None = None,
        end_block: int | None = None,
    ) -> str:

        if i is not None and (start_block is not None or end_block is not None):
            raise Exception('specify either job or start_block and end_block')
        elif i is not None:
            job = self.get_job_data(i)
            start = job['start_block']
            end = job['end_block']
        elif start_block is not None and end_block is not None:
            start = start_block
            end = end_block
        else:
            raise Exception('specify either job or start_block and end_block')

        return '{start_block:08d}_to_{end_block:08d}'.format(
            start_block=start,
            end_block=end,
        )

    #
    # # summary
    #

    def print_conclusion_section(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        duration = kwargs['end_time'] - kwargs['start_time']
        n_blocks = len(kwargs['jobs']) * self.chunk_size
        bps = n_blocks / duration
        print()
        print('- blocks covered:', toolstr.format(n_blocks))
        print('- blocks per second:', toolstr.format(bps, decimals=2))
        print('- blocks per minute:', toolstr.format(bps * 60, decimals=2))
        print('- blocks per hour:', toolstr.format(bps * 60 * 60, decimals=2))
        print('- blocks per day:', toolstr.format(bps * 86400, decimals=2))

    def summarize_blocks_per_second(
        self, sample_time: int = 60
    ) -> pl.DataFrame:
        jobs_per_second = self.summarize_jobs_per_second(
            sample_time=sample_time
        )
        start_blocks = [
            self.get_job_data(i)['start_block']
            for i in range(self.get_n_jobs())
        ]
        columns: typing.Sequence[pl.type_aliases.IntoExpr] = [
            pl.Series(start_blocks).alias('start_block'),
            (pl.col('jobs_per_second') * self.chunk_size).alias(
                'blocks_per_second'
            ),
        ]
        return jobs_per_second.with_columns(columns)

    def plot_blocks_per_second(self, sample_time: int = 60) -> None:
        import matplotlib.pyplot as plt  # type: ignore
        import toolplot  # type: ignore

        df = self.summarize_blocks_per_second(sample_time=sample_time)

        plt.plot(df['start_block'], df['blocks_per_second'])
        toolplot.add_tick_grid()
        toolplot.format_yticks()
        toolplot.format_xticks()
        plt.ylabel('blocks per second')
        plt.title('Tracing speed at different points in history')
        plt.xlabel('block number')

