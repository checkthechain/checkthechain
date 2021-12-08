from ctc import evm
from ctc import rpc
from . import coracle_spec


async def async_get_pcv_stats(
    block=None, blocks=None, wrapper=False, provider=None
):

    if block is not None:
        block = evm.normalize_block(block=block)
    if blocks is not None:
        blocks = evm.normalize_blocks(blocks=blocks)

    # assemble kwargs
    to_address = coracle_spec.get_cora_address(
        wrapper, block=block, blocks=blocks
    )
    kwargs = {'to_address': to_address}
    provider = rpc.get_provider(provider)
    if provider['chunk_size'] is None:
        provider['chunk_size'] = 1

    # fetch results
    keys = ['pcv', 'user_fei', 'protocol_equity', 'valid']
    if block is not None or (block is None and blocks is None):
        result = await rpc.async_eth_call(
            function_name='pcvStats',
            block_number=block,
            provider=provider,
            **kwargs
        )
        return dict(zip(keys, result))

    elif blocks is not None:
        result = await rpc.async_batch_eth_call(
            function_name='pcvStats',
            block_numbers=blocks,
            provider=provider,
            **kwargs
        )

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

