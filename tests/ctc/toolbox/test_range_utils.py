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
    (
        (40_000, 100_000),
        [
            [0, 40_000],
            [45_000, 50_000],
            [60_000, 70_000],
            [80_000, 100_000],
        ],
        [
            [40_001, 44_999],
            [50_001, 59_999],
            [70_001, 79_999],
        ],
    ),
]


@pytest.mark.parametrize('test', range_gap_tests)
def test_get_range_gaps(test):
    (start, end), subranges, target = test
    actual = range_utils.get_range_gaps(
        start=start,
        end=end,
        subranges=subranges,
    )
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
    (
        [
            [12000000, 12099999],
            [12100000, 12199999],
            [12200000, 12299999],
            [12300000, 12399999],
            [12400000, 12499999],
            [12500000, 12599999],
            [12600000, 12699999],
            [12700000, 12799999],
            [12800000, 12899999],
            [12900000, 12999999],
            [13000000, 13099999],
            [13100000, 13199999],
            [13200000, 13299999],
            [13300000, 13399999],
            [13400000, 13499999],
            [13500000, 13599999],
            [13600000, 13699999],
            [13700000, 13799999],
            [13800000, 13899999],
            [13900000, 13999999],
            [14000000, 14000000],
        ],
        {'include_contiguous': True},
        [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 10),
            (10, 11),
            (11, 12),
            (12, 13),
            (13, 14),
            (14, 15),
            (15, 16),
            (16, 17),
            (17, 18),
            (18, 19),
            (19, 20),
        ],
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
    actual = range_utils.range_to_chunks(
        start=start,
        end=end,
        chunk_size=chunk_size,
        **kwargs,
    )
    assert target == actual
