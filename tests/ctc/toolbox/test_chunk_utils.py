import pytest

from ctc.toolbox import range_utils


# additional tests
# - start being 1<=, ==, and 1>= a round bound
range_to_chunks_examples = [
    [
        {'start': 39, 'end': 42, 'chunk_size': 1},
        [[39, 39], [40, 40], [41, 41], [42, 42]],
    ],
    [
        {'start': 39, 'end': 42, 'chunk_size': 1, 'round_bounds': True},
        [[39, 39], [40, 40], [41, 41], [42, 42]],
    ],
    [
        {
            'start': 39,
            'end': 42,
            'chunk_size': 1,
            'round_bounds': True,
            'trim_outer_bounds': True,
        },
        [[39, 39], [40, 40], [41, 41], [42, 42]],
    ],
    [
        {'start': 39, 'end': 42, 'chunk_size': 1, 'index': True},
        [[39, 40], [40, 41], [41, 42], [42, 43]],
    ],
    [
        {
            'start': 39,
            'end': 42,
            'chunk_size': 1,
            'index': True,
            'round_bounds': True,
        },
        [[39, 40], [40, 41], [41, 42], [42, 43]],
    ],
    [
        {
            'start': 39,
            'end': 42,
            'chunk_size': 1,
            'index': True,
            'round_bounds': True,
            'trim_outer_bounds': True,
        },
        [[39, 40], [40, 41], [41, 42], [42, 43]],
    ],
    #
    #
    #
    [
        {'start': 390, 'end': 710, 'chunk_size': 100},
        [[390, 489], [490, 589], [590, 689], [690, 710]],
    ],
    [
        {'start': 390, 'end': 710, 'chunk_size': 100, 'round_bounds': True},
        [[300, 399], [400, 499], [500, 599], [600, 699], [700, 799]],
    ],
    [
        {
            'start': 390,
            'end': 710,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
        },
        [[390, 399], [400, 499], [500, 599], [600, 699], [700, 710]],
    ],
    [
        {'start': 390, 'end': 710, 'chunk_size': 100, 'index': True},
        [[390, 490], [490, 590], [590, 690], [690, 711]],
    ],
    [
        {
            'start': 390,
            'end': 710,
            'chunk_size': 100,
            'round_bounds': True,
            'index': True,
        },
        [[300, 400], [400, 500], [500, 600], [600, 700], [700, 800]],
    ],
    [
        {
            'start': 390,
            'end': 710,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
            'index': True,
        },
        [[390, 400], [400, 500], [500, 600], [600, 700], [700, 711]],
    ],
    #
    #
    #
    [
        {'start': 390, 'end': 699, 'chunk_size': 100},
        [[390, 489], [490, 589], [590, 689], [690, 699]],
    ],
    [
        {'start': 390, 'end': 699, 'chunk_size': 100, 'round_bounds': True},
        [[300, 399], [400, 499], [500, 599], [600, 699]],
    ],
    [
        {
            'start': 390,
            'end': 699,
            'chunk_size': 100, 'round_bounds': True,
            'trim_outer_bounds': True,
        },
        [[390, 399], [400, 499], [500, 599], [600, 699]],
    ],
    [
        {'start': 390, 'end': 699, 'chunk_size': 100, 'index': True},
        [[390, 490], [490, 590], [590, 690], [690, 700]],
    ],
    [
        {
            'start': 390,
            'end': 699,
            'chunk_size': 100,
            'round_bounds': True,
            'index': True,
        },
        [[300, 400], [400, 500], [500, 600], [600, 700]],
    ],
    [
        {
            'start': 390,
            'end': 699,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
            'index': True,
        },
        [[390, 400], [400, 500], [500, 600], [600, 700]],
    ],
    #
    #
    #
    [
        {'start': 390, 'end': 700, 'chunk_size': 100},
        [[390, 489], [490, 589], [590, 689], [690, 700]],
    ],
    [
        {'start': 390, 'end': 700, 'chunk_size': 100, 'round_bounds': True},
        [[300, 399], [400, 499], [500, 599], [600, 699], [700, 799]],
    ],
    [
        {
            'start': 390,
            'end': 700,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
        },
        [[390, 399], [400, 499], [500, 599], [600, 699], [700, 700]],
    ],
    [
        {'start': 390, 'end': 700, 'chunk_size': 100, 'index': True},
        [[390, 490], [490, 590], [590, 690], [690, 701]],
    ],
    [
        {
            'start': 390,
            'end': 700,
            'chunk_size': 100,
            'round_bounds': True,
            'index': True,
        },
        [[300, 400], [400, 500], [500, 600], [600, 700], [700, 800]],
    ],
    [
        {
            'start': 390,
            'end': 700,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
            'index': True,
        },
        [[390, 400], [400, 500], [500, 600], [600, 700], [700, 701]],
    ],
    #
    #
    #
    [
        {'start': 390, 'end': 701, 'chunk_size': 100},
        [[390, 489], [490, 589], [590, 689], [690, 701]],
    ],
    [
        {'start': 390, 'end': 701, 'chunk_size': 100, 'round_bounds': True},
        [[300, 399], [400, 499], [500, 599], [600, 699], [700, 799]],
    ],
    [
        {
            'start': 390,
            'end': 701,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
        },
        [[390, 399], [400, 499], [500, 599], [600, 699], [700, 701]],
    ],
    [
        {'start': 390, 'end': 701, 'chunk_size': 100, 'index': True},
        [[390, 490], [490, 590], [590, 690], [690, 702]],
    ],
    [
        {
            'start': 390,
            'end': 701,
            'chunk_size': 100,
            'round_bounds': True,
            'index': True,
        },
        [[300, 400], [400, 500], [500, 600], [600, 700], [700, 800]],
    ],
    [
        {
            'start': 390,
            'end': 701,
            'chunk_size': 100,
            'round_bounds': True,
            'trim_outer_bounds': True,
            'index': True,
        },
        [[390, 400], [400, 500], [500, 600], [600, 700], [700, 702]],
    ],
]


@pytest.mark.parametrize('example', range_to_chunks_examples)
def test_range_to_chunks(example):
    kwargs, target = example
    actual = range_utils.range_to_chunks(**kwargs)
    assert actual == target
