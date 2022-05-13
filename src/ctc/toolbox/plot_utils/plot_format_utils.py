from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

import matplotlib.pyplot as plt
import toolstr

from ctc import evm
from ctc import spec


async def async_block_timestamp_xticks(
    provider: spec.ProviderSpec = None,
    representation: tooltime.TimestampRepresentation | None = None,
):
    """
    matplotlib.FuncFormatter not used, because it cannot use async
    """

    raw_blocks, labels = plt.xticks()
    blocks = [int(block) for block in raw_blocks]
    block_timestamps = await evm.async_predict_block_timestamps(
        blocks, provider=provider
    )

    if representation is None:
        if len(block_timestamps) < 2:
            representation = 'TimestampDate'
        else:
            interval = block_timestamps[1] - block_timestamps[0]
            if interval > 86400:
                representation = 'TimestampDate'
            else:
                representation = 'TimestampISO'

    labels = [
        toolstr.format(
            timestamp,
            format_type='timestamp',
            representation=representation,
        )
        for timestamp in block_timestamps
    ]
    plt.xticks(raw_blocks, labels)
