import typing

from ctc import spec


def bin_by_blocks(
    data: spec.DataFrame,
    blocks: typing.Sequence[typing.SupportsInt],
    block_index_name: typing.Optional[str]='block_number',
) -> spec.DataFrame:
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
                data = typing.cast(spec.DataFrame, data.droplevel(index_name))

    standard_blocks = [int(block) for block in blocks]
    data = data.groupby(np.digitize(data.index.values, standard_blocks)).sum()
    data = pd.Series([0] * len(blocks), index=range(1, len(blocks) + 1)).add(
        data, fill_value=0
    )
    data.index = standard_blocks
    data.index.name = 'after_this_block'  # type: ignore

    return data

