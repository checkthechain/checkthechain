import typing

from ctc import spec


T = typing.TypeVar('T', spec.DataFrame, spec.Series)


def bin_by_blocks(
    data: T,
    blocks: typing.Sequence[typing.SupportsInt],
    block_index_name: typing.Optional[str] = 'block_number',
) -> T:
    """TODO: deprecate
    - either:
        - refactor using pd.cut() https://stackoverflow.com/a/33761120
        - kill this whole function
    """
    import numpy as np
    import pandas as pd

    if block_index_name is not None and len(data.index.names) > 1:
        for index_name in data.index.names:
            if index_name != 'block_number':
                data.index = data.index.droplevel(index_name)

    standard_blocks = [int(block) for block in blocks]
    new_data = data.groupby(
        np.digitize(data.index.values, standard_blocks)
    ).sum()
    new_data = pd.Series(
        [0] * len(blocks), index=range(1, len(blocks) + 1)
    ).add(new_data, fill_value=0)
    # if new_data.index[0] < standard_blocks[0]:
    #     new_data = new_data.iloc[1:]
    new_data.index = pd.Index(standard_blocks)
    new_data.index.name = 'gte_this_block'  # type: ignore

    return new_data

