"""
range bounds are **inclusive** by default
- can be switched to python-index-style ranges using index=True
"""
from __future__ import annotations

import math
import typing

if typing.TYPE_CHECKING:
    Range = typing.Sequence[int]

    T = typing.TypeVar('T')


def split(
    items: typing.Sequence[T],
    n_splits: int | None = None,
    *,
    items_per_split: int | None = None,
    exact: bool = False,
) -> typing.Sequence[typing.Sequence[T]]:

    if n_splits is not None and items_per_split is not None:
        raise Exception('specify either n_splits or items_per_split')

    elif n_splits is not None:

        n_items = len(items)
        items_per_split = math.floor(n_items / n_splits)

        if exact and n_items != n_splits * items_per_split:
            raise Exception('n_splits does not exactly divide items')

        sizes = [items_per_split] * n_splits

        remaining = n_items - items_per_split * n_splits
        for r in range(remaining):
            sizes[r] += 1

        splits = []
        current = 0
        for size in sizes:
            next = current + size
            sl = slice(current, next)
            splits.append(items[sl])
            current = next

        return splits

    elif items_per_split is not None:
        n_items = len(items)
        n_splits = math.ceil(n_items / items_per_split)
        if exact and n_items != n_splits * items_per_split:
            raise Exception('n_splits does not exactly divide items')
        splits = []
        for s in range(n_splits):
            sl = slice(s * items_per_split, (s + 1) * items_per_split)
            splits.append(items[sl])
        return splits

    else:
        raise Exception('specify either n_splits or items_per_split')


def get_range_gaps(
    *,
    start: int,
    end: int,
    subranges: typing.Sequence[Range],
) -> typing.Sequence[Range]:
    """get gaps between subranges of a given range"""

    if len(subranges) == 0:
        return [[start, end]]

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
    if current_start < end:
        gap_ranges.append([current_start, end])

    if (
        len(gap_ranges) > 0
        and gap_ranges[-1][-1] < end
        and subranges[-1][-1] < end
    ):
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

    connections: typing.Mapping[int, set[int]] = {
        r: set() for r in range(len(ranges))
    }
    for i, j in overlapping_ranges:
        connections[i].add(j)
        connections[j].add(i)

    group_of_each_range: typing.MutableMapping[int, set[int]] = {}
    for r in range(len(ranges)):

        # check which groups its neighbors are in
        groups_of_range = set()
        for other_r in connections[r]:
            if other_r in group_of_each_range:
                groups_of_range.add(other_r)

        group = {r}
        if len(groups_of_range) == 0:
            # if no neighbors are in groups, create a new one
            group |= set(connections[r])

        else:
            # if neighbors are in groups, combine those groups
            for other_r in groups_of_range:
                group |= group_of_each_range[other_r]

        for i in group:
            group_of_each_range[i] = group

    unique_groups = set(tuple(group) for group in group_of_each_range.values())

    combined_ranges = []
    for group_rs in unique_groups:
        range_start = min(ranges[group_range][0] for group_range in group_rs)
        range_end = max(ranges[group_range][1] for group_range in group_rs)
        combined_ranges.append([range_start, range_end])

    return combined_ranges


# def combine_overlapping_ranges(
#     ranges: typing.Sequence[Range],
#     *,
#     include_contiguous: bool = False,
# ) -> typing.Sequence[Range]:
#     """combine ranges as needed to produce list of non-overlapping ranges"""

#     print("RANGES (" + str(len(ranges)) + ')', ranges)
#     print()

#     overlapping_ranges = get_overlapping_ranges(
#         ranges,
#         include_contiguous=include_contiguous,
#     )

#     if len(overlapping_ranges) == 0:
#         return ranges

#     else:
#         combined_ranges = []
#         for i, j in overlapping_ranges:
#             combined_start = min(ranges[i][0], ranges[j][0])
#             combined_end = max(ranges[i][1], ranges[j][1])
#             combined_ranges.append([combined_start, combined_end])
#         fixed_ranges = combine_overlapping_ranges(
#             combined_ranges,
#             include_contiguous=include_contiguous,
#         )

#         overlapping_indices = {index for r in overlapping_ranges for index in r}
#         nonoverlapping_ranges = [
#             range
#             for r, range in enumerate(ranges)
#             if r not in overlapping_indices
#         ]

#         return nonoverlapping_ranges + list(fixed_ranges)


def range_to_chunks(
    *,
    start: int,
    end: int,
    chunk_size: int,
    round_bounds: bool = False,
    trim_outer_bounds: bool = False,
    index: bool = False,
) -> typing.Sequence[typing.Sequence[int]]:
    """break a range into chunks of a given chunk size

    ## Examples
    1. range_to_chunks(start=390, end=710, chunk_size=100)
        --> [[390, 489], [490, 589], [590, 689], [690, 710]]
    2. range_to_chunks(start=390, end=710, chunk_size=100, round_bounds=True)
        --> [[300, 399], [400, 499], [500, 599], [600, 699], [700, 799]
    3. range_to_chunks(start=390, end=710, chunk_size=100, round_bounds=True, trim_outer_bounds=True)
        --> [[390, 399], [400, 499], [500, 599], [600, 699], [700, 710]
    4. range_to_chunks(start=390, end=710, chunk_size=100, index=True)
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

