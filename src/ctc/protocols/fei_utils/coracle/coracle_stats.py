from __future__ import annotations

import asyncio
import typing
from typing_extensions import TypedDict

from ctc import evm
from ctc import rpc
from ctc import spec
from . import coracle_spec


class FeiPcvStats(TypedDict):
    pcv: int
    user_fei: int
    protocol_equity: int
    valid: bool


async def async_get_pcv_stats(
    block: spec.BlockNumberReference | None = None,
    wrapper: bool = False,
    provider: spec.ProviderSpec = None,
) -> FeiPcvStats:

    if block is None:
        block = 'latest'
    if block is not None:
        block = await evm.async_block_number_to_int(block=block)

    to_address = coracle_spec.get_coracle_address(
        wrapper,
        block=block,
    )
    result = await rpc.async_eth_call(
        function_name='pcvStats',
        block_number=block,
        provider=provider,
        to_address=to_address,
    )
    return {
        'pcv': result[0],
        'user_fei': result[1],
        'protocol_equity': result[2],
        'valid': result[3],
    }


async def async_get_pcv_stats_by_block(
    blocks: typing.Sequence[spec.BlockNumberReference],
    wrapper: bool = False,
    provider: spec.ProviderSpec = None,
) -> spec.DataFrame:

    import numpy as np

    if blocks is not None:
        blocks = await evm.async_block_numbers_to_int(blocks=blocks)

    # assemble kwargs
    provider = rpc.get_provider(provider)
    if provider['chunk_size'] is None:
        provider['chunk_size'] = 1

    coroutines = []
    for block in blocks:
        to_address = coracle_spec.get_coracle_address(
            wrapper,
            block=block,
        )
        coroutine = rpc.async_eth_call(
            function_name='pcvStats',
            block_number=block,
            provider=provider,
            to_address=to_address,
        )
        coroutines.append(coroutine)
    result = await asyncio.gather(*coroutines)

    # arrange results
    transpose = list(zip(*result))
    data = {}
    keys = ['pcv', 'user_fei', 'protocol_equity', 'valid']
    for k, key in enumerate(keys):
        data[key] = transpose[k]

    as_array = {
        'pcv': np.array(data['pcv']) / 1e18,
        'user_fei': np.array(data['user_fei']) / 1e18,
        'protocol_equity': np.array(data['protocol_equity']) / 1e18,
        'valid': data['valid'],
    }

    # create dataframe
    import pandas as pd

    df = pd.DataFrame(as_array, index=blocks)

    return df

