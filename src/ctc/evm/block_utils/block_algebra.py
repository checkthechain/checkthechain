# need to update many of these functions
# need to not import pandas at top level

import pandas as pd
import numpy as np


# contenttypes = {
#     'BlockSeries': [
#         {'start_block': 'BlockNumber', 'end_block': 'BlockNumber'},
#         {'blocks': ['BlockNumber'], 'values': ['Any']},
#         {'BlockNumber': 'Any'},
#         ['BlockNumber'],
#         {'__type': 'DataFrame'},
#     ]
# }


def interpolate_block_series(
    *,
    series=None,
    as_dict=None,
    blocks=None,
    values=None,
    end_block=None,
    output_format=None,
):
    """should probably turn this into a content-agnostic pandas function"""

    #
    if output_format is None:
        if series is not None:
            output_format = 'series'
        elif as_dict is not None:
            output_format = 'dict'
        else:
            raise Exception('could not determine output format')

    # extract blocks and values
    if blocks is None and values is None:
        if series is not None:
            blocks = series.index
            values = series.values
        elif as_dict is not None:
            blocks = list(as_dict.keys())
            values = list(as_dict.values())
        else:
            raise Exception('must specify series, as_dict, or {blocks, values}')

    # initialize datastructures
    if end_block is None:
        end_block = blocks[-1]
    interpolated_blocks = np.arange(blocks[0], end_block + 1, 1, dtype=int)
    interpolated_values = np.zeros(
        len(interpolated_blocks), dtype=type(values[0])
    )

    # interpolate values
    blocks_to_values = dict(zip(blocks, values))
    current_value = values[0]
    for b, block in enumerate(interpolated_blocks):
        if block in blocks_to_values:
            current_value = blocks_to_values[block]
        interpolated_values[b] = current_value

    # format output
    if output_format == 'series':
        return pd.Series(interpolated_values, index=interpolated_blocks)
    elif output_format == 'dict':
        return dict(zip(interpolated_blocks, interpolated_values))
    elif output_format == 'array':
        return {
            'blocks': interpolated_blocks,
            'values': interpolated_values,
        }
    else:
        raise Exception('unknown output format: ' + str(output_format))


# def intersect_block_ranges(series_list):

#     bounds = get_block_ranges_bounds(series_list)
#     start_block = max(bounds['start_blocks'])
#     end_block = min(bounds['end_blocks'])

#     if start_block > end_block:
#         raise Exception('intersection is empty')

#     return {
#         'start_block': start_block,
#         'end_block': end_block,
#     }


# def union_block_ranges(series_list):
#     bounds = get_block_ranges_bounds(series_list)

#     return {
#         'start_block': min(bounds['start_blocks']),
#         'end_block': max(bounds['end_blocks']),
#     }


# def get_block_ranges_bounds(series_list):
#     start_blocks = []
#     end_blocks = []
#     for series in series_list:
#         series_bounds = get_block_range_bounds(series)
#         start_blocks.append(series_bounds['start_block'])
#         end_blocks.append(series_bounds['end_block'])
#     return {'start_blocks': start_blocks, 'end_blocks': end_blocks}


# def get_block_range_bounds(series):
#     if isinstance(series, (np.ndarray, list)):
#         start_block = min(series)
#         end_block = max(series)
#     elif isinstance(series, dict):
#         if 'blocks' in series:
#             start_block = min(series['blocks'])
#             end_block = max(series['blocks'])
#         elif 'start_block' in series and 'end_block' in series:
#             start_block = series['start_block']
#             end_block = series['end_block']
#         elif all(isinstance(key, int) for key in series.keys()):
#             start_block = min(series.keys())
#             end_block = max(series.keys())
#         else:
#             raise Exception()
#     elif isinstance(series, pd.DataFrame):
#         raise NotImplementedError()
#     else:
#         raise Exception('unknown series format: ' + str(type(series)))

#     return {'start_block': start_block, 'end_block': end_block}


# def trim_to_range(series, start_block, end_block):
#     if isinstance(series, dict):
#         if 'blocks' in series:
#             mask = (series['blocks'] >= start_block) * (
#                 series['blocks'] <= end_block
#             )
#             return {
#                 'blocks': series['blocks'][mask],
#                 'values': series['values'][mask],
#             }

#         elif 'start_block' in series and 'end_block' in series:
#             new_start_block = max(start_block, series['start_block'])
#             new_end_block = min(end_block, series['end_block'])
#             return {'start_block': new_start_block, 'end_block': new_end_block}
#         elif all(isinstance(key, int) for key in series.keys()):
#             return {
#                 block: datum
#                 for block, datum in series.items()
#                 if start_block <= block and block <= end_block
#             }
#         else:
#             raise Exception()
#     elif isinstance(series, pd.DataFrame):
#         raise NotImplementedError()
#     else:
#         raise Exception()

