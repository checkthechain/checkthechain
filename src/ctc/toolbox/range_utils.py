"""
range bounds are **inclusive** by default
- can be switched to python-index-style ranges using index=True
"""
from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    Range = typing.Sequence[int]


def get_range_gaps(
    start: int,
    end: int,
    subranges: typing.Sequence[Range],
) -> typing.Sequence[Range]:
    """get gaps between subranges of a given range"""

    # make ranges non-overlapping
    subranges = combine_overlapping_ranges(subranges)

    # sort subranges
    subranges = sorted(subranges, key=lambda subrange: subrange[0])

    # get gap ranges
    gap_ranges = []
    current_start = start
    for substart, subend in subranges:

        # skip subranges that fall out of main range
        if subend < current_start:
            continue
        if substart > end:
            break

        if substart <= current_start and subend >= current_start:
            current_start = subend + 1
            continue
        else:
            gap_range = [current_start, substart - 1]
            gap_ranges.append(gap_range)
            current_start = subend + 1

    if gap_ranges[-1][-1] < end:
        gap_range = [subend + 1, end]
        gap_ranges.append(gap_range)

    return gap_ranges


def get_overlapping_ranges(
    ranges: typing.Sequence[Range],
    *,
    include_contiguous: bool = False,
) -> typing.Sequence[tuple[int, int]]:
    """get pairs of ranges that have overlap

    if include_contiguous, then consider touching ranges to be overlapping
    """

    overlapping_ranges = []
    for i, (start, end) in enumerate(ranges):
        other_slice = i + 1
        for j, (other_start, other_end) in list(enumerate(ranges))[
            other_slice:
        ]:
            if start <= other_end and other_start <= end:
                overlapping_ranges.append((i, j))
            elif include_contiguous and (
                start == other_end + 1 or other_start == end + 1
            ):
                overlapping_ranges.append((i, j))
    return overlapping_ranges


def combine_overlapping_ranges(
    ranges: typing.Sequence[Range],
    *,
    include_contiguous: bool = False,
) -> typing.Sequence[Range]:
    """combine ranges as needed to produce list of non-overlapping ranges"""

    overlapping_ranges = get_overlapping_ranges(
        ranges,
        include_contiguous=include_contiguous,
    )

    if len(overlapping_ranges) == 0:
        return ranges

    else:
        combined_ranges = []
        for i, j in overlapping_ranges:
            combined_start = min(ranges[i][0], ranges[j][0])
            combined_end = max(ranges[i][1], ranges[j][1])
            combined_ranges.append([combined_start, combined_end])
        fixed_ranges = combine_overlapping_ranges(
            combined_ranges,
            include_contiguous=include_contiguous,
        )

        overlapping_indices = {index for r in overlapping_ranges for index in r}
        nonoverlapping_ranges = [
            range
            for r, range in enumerate(ranges)
            if r not in overlapping_indices
        ]

        return nonoverlapping_ranges + list(fixed_ranges)


def range_to_chunks(
    start: int,
    end: int,
    chunk_size: int,
    *,
    round_bounds: bool = False,
    trim_outer_bounds: bool = False,
    index: bool = False,
) -> typing.Sequence[typing.Sequence[int]]:
    """break a range into chunks of a given chunk size

    ## Examples
    1. range_to_chunks(390, 710, 100)
        --> [[390, 489], [490, 589], [590, 689], [690, 710]]
    2. range_to_chunks(390, 710, 100, round_bounds=True)
        --> [[300, 399], [400, 499], [500, 599], [600, 699], [700, 799]
    3. range_to_chunks(390, 710, 100, round_bounds=True, trim_outer_bounds=True)
        --> [[390, 399], [400, 499], [500, 599], [600, 699], [700, 710]
    4. range_to_chunks(390, 710, 100, index=True)
        --> [[390, 490], [490, 590], [590, 690], [690, 711]]

    ## Inputs
    - start
    - end
    - chunk_size
    - round_bounds: round lower down and upper up to reach standardized bounds
    - trim_outer_bounds: trim standardized bounds to not exceed original inputs
        - has no effect unless round_bounds=True
    - index: return ranges that can be used as python indices (end = end + 1)
    """

    # compute range bounds
    if round_bounds:
        start_bound = (start // chunk_size) * chunk_size
        end_bound = ((end // chunk_size) + 1) * chunk_size
        bounds = list(range(start_bound, end_bound + 1, chunk_size))
    else:
        bounds = list(range(start, end + 1, chunk_size))
        bounds.append(end + 1)

    # create chunks
    chunks = []
    for bound_start, bound_end in zip(bounds[:-1], bounds[1:]):
        if index:
            chunk = [bound_start, bound_end]
        else:
            chunk = [bound_start, bound_end - 1]
        chunks.append(chunk)

    # trim outer bounds if needed
    if trim_outer_bounds:
        if len(chunks) > 0:

            if chunks[0][0] < start:
                chunks[0] = [start, chunks[0][1]]

            if index:
                last_value = end + 1
            else:
                last_value = end
            if chunks[-1][-1] > last_value:
                chunks[-1] = [chunks[-1][0], last_value]

    return chunks
