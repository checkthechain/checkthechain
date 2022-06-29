from __future__ import annotations

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
    *,
    wrapper: bool = False,
    provider: spec.ProviderReference = None,
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
    *,
    wrapper: bool = False,
    provider: spec.ProviderReference = None,
    nullify_invalid: bool = True,
) -> spec.DataFrame:

    import asyncio
    import numpy as np

    if blocks is not None:
        blocks = await evm.async_block_numbers_to_int(blocks=blocks)

    # assemble kwargs
    provider = rpc.get_provider(provider)
    if provider['chunk_size'] is None:
        provider['chunk_size'] = 1

    async def _wrapped_call(
        block: spec.BlockNumberReference, to_address: spec.Address
    ) -> typing.Sequence[None | list[typing.Any]]:
        try:
            result = await rpc.async_eth_call(
                function_name='pcvStats',
                block_number=block,
                provider=provider,
                to_address=to_address,
            )
            return typing.cast(
                typing.Sequence[typing.Optional[typing.List[typing.Any]]],
                result,
            )
        except spec.RpcException as e:
            invalid_message = 'execution reverted: chainlink is down'
            if (
                nullify_invalid
                and len(e.args) > 0
                and e.args[0].endswith(invalid_message)
            ):
                return [None] * 4
            else:
                raise e

    coroutines = []
    for block in blocks:
        to_address = coracle_spec.get_coracle_address(
            wrapper,
            block=block,
        )
        coroutine = _wrapped_call(block, to_address)
        coroutines.append(coroutine)
    result = await asyncio.gather(*coroutines)

    # arrange results
    transpose = list(zip(*result))
    data = {}
    keys = ['pcv', 'user_fei', 'protocol_equity', 'valid']
    for k, key in enumerate(keys):
        data[key] = transpose[k]

    as_array = {
        'pcv': np.array(data['pcv'], dtype=float) / 1e18,
        'user_fei': np.array(data['user_fei'], dtype=float) / 1e18,
        'protocol_equity': np.array(data['protocol_equity'], dtype=float)
        / 1e18,
        'valid': data['valid'],
    }

    # create dataframe
    import pandas as pd

    df = pd.DataFrame(as_array, index=blocks)

    return df
