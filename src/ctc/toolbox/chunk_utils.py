from __future__ import annotations

import typing


def range_to_chunks(
    start: int,
    end: int,
    chunk_size: int,
    *,
    round_bounds: bool = False,
    trim_outer_bounds: bool = False,
    index: bool = False
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
        --> [[390, 490], [490, 590], [590, 690], [690, 710]]

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
