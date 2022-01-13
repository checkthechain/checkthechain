import asyncio

from ctc import evm
from ctc import rpc
from . import coracle_spec


async def async_get_pcv_stats(
    block=None, blocks=None, wrapper=False, provider=None
):

    if block is not None:
        block = await evm.async_block_number_to_int(block=block)
    if blocks is not None:
        blocks = await evm.async_block_numbers_to_int(blocks=blocks)

    # assemble kwargs
    provider = rpc.get_provider(provider)
    if provider['chunk_size'] is None:
        provider['chunk_size'] = 1

    # fetch results
    keys = ['pcv', 'user_fei', 'protocol_equity', 'valid']
    if block is not None or (block is None and blocks is None):
        to_address = coracle_spec.get_coracle_address(
            wrapper, block=block,
        )
        result = await rpc.async_eth_call(
            function_name='pcvStats',
            block_number=block,
            provider=provider,
            to_address=to_address,
        )
        return dict(zip(keys, result))

    elif blocks is not None:
        coroutines = []
        for block in blocks:
            to_address = coracle_spec.get_coracle_address(
                wrapper, block=block,
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
        for k, key in enumerate(keys):
            data[key] = transpose[k]
            import numpy as np

            data[key] = np.array(data[key])
            if key in ['pcv', 'user_fei', 'protocol_equity']:
                data[key] = data[key] / 1e18

        # create dataframe
        import pandas as pd

        df = pd.DataFrame(data, index=blocks)

        return df

    else:
        raise Exception('must specify block or blocks')

