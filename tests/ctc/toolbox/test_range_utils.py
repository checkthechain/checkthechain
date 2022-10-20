from __future__ import annotations

import pytest

from ctc.toolbox import range_utils


# given as tuples of (range, previous_queries, desired_output)
range_gap_tests = [
    (
        (40_000, 100_000),
        [
            [45_000, 50_000],
            [60_000, 70_000],
            [80_000, 90_000],
        ],
        [
            [40_000, 44_999],
            [50_001, 59_999],
            [70_001, 79_999],
            [90_001, 100_000],
        ],
    ),
    (
        (40_000, 100_000),
        [
            [0, 42_000],
            [45_000, 50_000],
            [60_000, 70_000],
            [80_000, 90_000],
        ],
        [
            [42_001, 44_999],
            [50_001, 59_999],
            [70_001, 79_999],
            [90_001, 100_000],
        ],
    ),
    (
        (40_000, 100_000),
        [
            [0, 40_000],
            [45_000, 50_000],
            [60_000, 70_000],
            [80_000, 90_000],
        ],
        [
            [40_001, 44_999],
            [50_001, 59_999],
            [70_001, 79_999],
            [90_001, 100_000],
        ],
    ),
]


@pytest.mark.parametrize('test', range_gap_tests)
def test_get_range_gaps(test):
    (start, end), subranges, target = test
    actual = range_utils.get_range_gaps(start, end, subranges)
    assert actual == target


overlapping_range_tests = [
    (
        [
            [3, 6],
            [6, 10],
            [11, 20],
        ],
        {'include_contiguous': True},
        [(0, 1), (1, 2)],
    ),
    (
        [
            [3, 6],
            [6, 10],
            [11, 20],
        ],
        {'include_contiguous': False},
        [(0, 1)],
    ),
]


@pytest.mark.parametrize('test', overlapping_range_tests)
def test_get_overlapping_ranges(test):
    ranges, kwargs, target = test
    actual = range_utils.get_overlapping_ranges(ranges, **kwargs)
    assert actual == target


# start, end, chunk_size, kwargs, target
range_to_chunk_tests = [
    (
        390,
        710,
        100,
        {},
        [[390, 489], [490, 589], [590, 689], [690, 710]],
    ),
    (
        390,
        710,
        100,
        {'round_bounds': True},
        [[300, 399], [400, 499], [500, 599], [600, 699], [700, 799]],
    ),
    (
        390,
        710,
        100,
        {'round_bounds': True, 'trim_outer_bounds': True},
        [[390, 399], [400, 499], [500, 599], [600, 699], [700, 710]],
    ),
    (
        390,
        710,
        100,
        {'index': True},
        [[390, 490], [490, 590], [590, 690], [690, 711]],
    ),
]


@pytest.mark.parametrize('test', range_to_chunk_tests)
def test_range_to_chunks(test):
    start, end, chunk_size, kwargs, target = test
    actual = range_utils.range_to_chunks(start, end, chunk_size, **kwargs)
    assert target == actual
