from ctc import spec


def bin_by_blocks(
    data: 'pandas.DataFrame', blocks: list[spec.BlockReference]
) -> 'pandas.DataFrame':
    import numpy as np
    import pandas as pd

    if len(data.index.names) > 1:
        for index_name in data.index.names:
            if index_name != 'block_number':
                data = data.droplevel(index_name)

    data = data.groupby(np.digitize(data.index.values, blocks)).sum()
    data = pd.Series([0] * len(blocks), index=range(1, len(blocks) + 1)).add(
        data, fill_value=0
    )
    data.index = blocks
    data.index.name = 'after_this_block'

    return data

