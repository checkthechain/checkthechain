import pytest

from ctc import evm


# output, series, as_dict, blocks, values, end_block, output_format
test_interpolations = [
    [
        {
            100: 50,
            101: 50,
            102: 50,
            103: 50,
            104: 50,
            105: 43,
            106: 43,
            107: 43,
            108: 43,
            109: 67,
            110: 67,
            111: 67,
        },
        None,
        {100: 50, 105: 43, 109: 67},
        None,
        None,
        111,
        'dict',
    ],
]


@pytest.mark.parametrize('test', test_interpolations)
def test_interpolate_block_series(test):
    target_output, series, as_dict, blocks, values, end_block, output_format = test

    actual_output = evm.interpolate_block_series(
        series=series,
        as_dict=as_dict,
        blocks=blocks,
        values=values,
        end_block=end_block,
        output_format=output_format,
    )

    assert target_output == actual_output

