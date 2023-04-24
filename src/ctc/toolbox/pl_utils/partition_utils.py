"""functions related to file partitions

TODO:
- skipping files that already exist
- add partition column to name
"""

from __future__ import annotations

import glob
import os
import typing
import tempfile

import polars as pl
import toolstr

from ctc.toolbox import pl_utils
from ctc.toolbox import range_utils


def create_partition_bounds(
    n_partitions: int,
    n_bound_nibbles: int | None,
) -> typing.Sequence[int]:
    if n_bound_nibbles is None:
        if n_partitions <= 16:
            n_bound_nibbles = 1
        elif n_partitions <= 256:
            n_bound_nibbles = 2
        elif n_partitions <= 65536:
            n_bound_nibbles = 4
        elif n_partitions <= 16777216:
            n_bound_nibbles = 6
        elif n_partitions <= 4294967296:
            n_bound_nibbles = 8
        else:
            raise Exception('must specify number of nibbles')

    max_bound = 16**n_bound_nibbles
    interval_size = int(max_bound / n_partitions)
    bounds = list(range(0, max_bound + interval_size, interval_size))
    bounds = [value - 1 for value in bounds]
    return bounds


def repartition_files(
    *,
    method: typing.Literal['simple', 'chunked'],
    target: str | typing.Sequence[str],
    column: str,
    output_dir: str,
    input_template: str,
    output_template: str,
    template_aggregations: typing.Mapping[str, str],
    n_partitions: int,
    n_bound_nibbles: int,
    chunk_size: int | None = None,
    temporary_dir: str | None = None,
    delete_temporary: bool = True,
    n_row_groups_per_partition: int | None = None,
    row_group_size: int | None = None,
    verbose: bool | int = True,
    skip_existing: bool = False,
    columns_in_partition_names: bool = True,
) -> None:
    """
    Reindexing methods
    - simple
        - allowed when dataset fits in memory
        - uses 1 pass over the data for reading and writing
        - steps:
            - load all dataset files
            - sort data
            - partition data into files
    - chunked
        - required when dataset does not fit in memory
            - each chunk should fit in memory
        - uses 2 passes over the data for reading and writing
        - raw_files --> temporary_files --> final_files
        - for chunks of N dataset files:
            - load N dataset files
            - sort data
            - partition data into temporary files
        - for each partition of temporary files
            - load files
            - combine into single file
    """

    import time

    start = time.time()

    # get file chunks and temporary directory
    if isinstance(target, str):
        all_files = glob.glob(target)
        all_files = sorted(all_files)
    elif isinstance(target, list):
        all_files = target
    else:
        raise Exception('invalid target format')

    # create partition bounds and labels
    bounds = create_partition_bounds(
        n_partitions=n_partitions,
        n_bound_nibbles=n_bound_nibbles,
    )
    labels = [
        '0x'
        + hex(start + 1)[2:].rjust(n_bound_nibbles, '0')
        + '_to_0x'
        + hex(end)[2:].rjust(n_bound_nibbles, '0')
        for start, end in zip(bounds[:-1], bounds[1:])
    ]

    # create partitions
    if method == 'simple':
        _files_to_partitions(
            paths=all_files,
            bounds=bounds,
            labels=labels,
            column=column,
            output_dir=output_dir,
            input_template=input_template,
            output_template=output_template,
            skip_existing=skip_existing,
            columns_in_partition_names=columns_in_partition_names,
        )
    elif method == 'chunked':
        _repartition_files_chunked(
            all_files=all_files,
            bounds=bounds,
            labels=labels,
            column=column,
            input_template=input_template,
            output_template=output_template,
            template_aggregations=template_aggregations,
            output_dir=output_dir,
            n_bound_nibbles=n_bound_nibbles,
            n_partitions=n_partitions,
            chunk_size=chunk_size,
            temporary_dir=temporary_dir,
            delete_temporary=delete_temporary,
            n_row_groups_per_partition=n_row_groups_per_partition,
            row_group_size=row_group_size,
            verbose=verbose,
            skip_existing=skip_existing,
            columns_in_partition_names=columns_in_partition_names,
        )
    else:
        raise Exception('invalid method: ' + str(method))

    if verbose:
        end = time.time()
        print('took', '%.2f' % (end - start), 'seconds')


def _repartition_files_chunked(
    *,
    all_files: typing.Sequence[str],
    bounds: typing.Sequence[int],
    labels: typing.Sequence[str],
    column: str,
    output_dir: str,
    n_partitions: int,
    n_bound_nibbles: int | None,
    chunk_size: int | None,
    temporary_dir: str | None,
    delete_temporary: bool,
    template_aggregations: typing.Mapping[str, str],
    input_template: str,
    output_template: str,
    n_row_groups_per_partition: int | None,
    row_group_size: int | None,
    verbose: bool | int,
    skip_existing: bool,
    columns_in_partition_names: bool,
) -> None:
    if temporary_dir is None:
        temporary_dir = tempfile.mkdtemp()
    chunks = range_utils.split(all_files, items_per_split=chunk_size)

    # print summary
    if verbose:
        print(
            'Repartitioning',
            len(all_files),
            'files into',
            n_partitions,
            'files',
        )
        total_bytes = sum(os.stat(path).st_size for path in all_files)
        print('- total data:', toolstr.format_nbytes(total_bytes))
        if n_row_groups_per_partition is not None:
            print('- n_row_groups_per_partition:', n_row_groups_per_partition)
        elif row_group_size is not None:
            print('- row_group_size:', row_group_size)
        else:
            print('- using 1 row group per partition')
        original_dirs = {os.path.dirname(path) for path in all_files}
        if len(original_dirs) == 1:
            original_dir = next(iter(original_dirs))
        else:
            original_dir = '[multiple]'
        print()
        print('Directories')
        print('- original dir:', original_dir)
        print('- temporary dir:', temporary_dir)
        print('- final dir:', output_dir)
        print()
        print(
            'partitioning by column',
            column,
            'using',
            len(labels),
            'value ranges:',
        )
        labels_with_number: list[tuple[int | None, str | None]] = list(
            enumerate(labels)
        )
        show_partitions = 10
        if len(labels) > show_partitions:
            labels_with_number = (
                labels_with_number[: int(show_partitions / 2)]
                + [(None, None)]
                + labels_with_number[int(-show_partitions / 2) :]
            )
        for p, label in labels_with_number:
            if p is not None:
                print('    ' + str(p + 1) + '.', label)
            else:
                print('    ...')
        print()
        print('creating', len(chunks) * n_partitions, 'temporary files')
        if len(chunks) == 1:
            word = 'chunk'
        else:
            word = 'chunks'
        print(
            '- processing the original',
            len(all_files),
            'files in',
            len(chunks),
            word,
            'of',
            len(chunks[0]),
            'files each',
        )

    # convert each chunk into parititons
    paths_per_partition: typing.MutableMapping[str, list[str]] = {}
    for c, chunk in enumerate(chunks):
        if verbose:
            aggregations = toolstr.parse_aggregate_by_template(
                strs=chunk,
                template=input_template,
                aggregations=template_aggregations,
            )
            name = ', '.join(
                k + '=' + str(aggregations[k])
                for k in template_aggregations.keys()
            )
            print('processing chunk', c + 1, '/', str(len(chunks)) + ',', name)

        # get output_template
        partition_output_template = _combine_paths(
            paths=chunk,
            input_template=input_template,
            output_template=output_template,
            aggregations=template_aggregations,
            values={'partition': '{partition}'},
        )
        partition_output_template = os.path.join(
            temporary_dir,
            partition_output_template,
        )

        # perform partitioning
        chunk_paths_per_partition = _files_to_partitions(
            paths=chunk,
            bounds=bounds,
            labels=labels,
            column=column,
            output_dir=temporary_dir,
            input_template=input_template,
            output_template=partition_output_template,
            skip_existing=skip_existing,
            columns_in_partition_names=columns_in_partition_names,
        )

        # record file paths
        for key, value in chunk_paths_per_partition.items():
            paths_per_partition.setdefault(key, [])
            paths_per_partition[key].extend(value)

    # consolidate files of each partition
    if verbose:
        print()
        print('consolidating into final partitioned files')
    for p, partition in enumerate(paths_per_partition.keys()):
        partition_paths = paths_per_partition[partition]

        # get output_path
        output_path = _combine_paths(
            paths=partition_paths,
            input_template=output_template,
            output_template=output_template,
            aggregations=template_aggregations,
            values={},
        )
        output_path = os.path.join(output_dir, output_path)

        if skip_existing and os.path.isfile(output_path):
            if verbose:
                print(
                    'skipping',
                    partition,
                    '(partition',
                    str(p + 1) + ' / ' + str(len(labels)) + ')',
                )
            continue
        if verbose >= 2:
            print(
                'writing',
                partition,
                '(partition',
                str(p + 1) + ' / ' + str(len(labels)) + ')',
            )

        # load files and consolidate into single file
        df = pl.concat(
            [pl.read_parquet(path) for path in partition_paths]
        ).sort(column)
        pl_utils.write_df(
            df=df,
            path=output_path,
            n_row_groups=n_row_groups_per_partition,
            row_group_size=row_group_size,
            create_dir=True,
        )

    # delete temporary files
    if delete_temporary:
        if verbose:
            print()
            print('deleting temporary files')
        for partition, partition_paths in paths_per_partition.items():
            for path in partition_paths:
                os.remove(path)
    else:
        if verbose:
            print()
            print('not deleting temporary files')

    # print outro
    if verbose:
        print('reindexing complete')


def _files_to_partitions(
    *,
    paths: typing.Sequence[str],
    bounds: typing.Sequence[int],
    labels: typing.Sequence[str],
    column: str,
    output_dir: str,
    input_template: str,
    output_template: str,
    skip_existing: bool,
    columns_in_partition_names: bool,
) -> typing.MutableMapping[str, typing.Sequence[str]]:
    # create output paths
    paths_per_partition: typing.MutableMapping[str, typing.Sequence[str]] = {}
    for p, label in enumerate(labels):
        if columns_in_partition_names:
            partition_name = column + '_' + label
        else:
            partition_name = label
        paths_per_partition[label] = [
            output_template.format(partition=partition_name)
        ]

    # skip if paths already exist
    if skip_existing and all(
        os.path.isfile(path)
        for path_list in paths_per_partition.values()
        for path in path_list
    ):
        return paths_per_partition

    # load files
    df = pl.concat([pl.scan_parquet(path) for path in paths]).collect(
        streaming=True
    )

    # create cut labels
    n_bound_nibbles = len(labels[-1].split('_')[0]) - 2
    partition_values = (
        df[column]
        .bin.encode('hex')
        .str.slice(0, n_bound_nibbles)
        .apply(lambda x: int(x, 16))
    )

    # determine partition of each row
    binned_rows = partition_values.cut(
        bins=bounds,  # type: ignore
        labels=['UNDERFLOW'] + labels + ['OVERFLOW'],  # type: ignore
        maintain_order=True,
    )
    partitions = binned_rows['category'].cast(int)

    # write partitioned files, and record path of each partition
    for p, label in enumerate(labels):
        output_path = paths_per_partition[label][0]
        partition_df = df.filter(partitions == p + 1)
        pl_utils.write_df(
            df=partition_df,
            path=output_path,
            statistics=False,
            create_dir=True,
        )

    return paths_per_partition


def _combine_paths(
    *,
    paths: typing.Sequence[str],
    input_template: str,
    output_template: str,
    aggregations: typing.Mapping[str, str],
    values: typing.Mapping[str, str],
) -> str:
    """metadata should be separated by underscores"""

    output_values = toolstr.parse_aggregate_by_template(
        strs=paths,
        template=input_template,
        aggregations=aggregations,
    )

    if values is not None:
        output_values = dict(output_values, **values)

    return output_template.format(**output_values)

