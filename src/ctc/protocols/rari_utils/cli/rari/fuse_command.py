from __future__ import annotations

import toolcli

from ctc import evm
from ctc import rpc
from ctc import spec
from ctc.protocols import rari_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_fuse_command,
        'help': 'summarize fuse pool, token, or platform',
        'args': [
            # TODO: allow arg to be pool comptroller
            # - will need to check on chain to see if token or comptroller
            {
                'name': 'arg',
                'nargs': '?',
                'help': 'pool index or token, omit to summarize platform',
            },
            {'name': '--block', 'default': 'latest', 'help': 'block number'},
        ],
        'examples': {
            '8': {'description': 'summarize a pool'},
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca': {
                'description': 'summarize a token across all pools',
                'long': True,
            },
            '': {'description': 'summarize all of Rari', 'long': True},
        },
    }


async def async_fuse_command(arg: str, block: str) -> None:
    block_number = await evm.async_block_number_to_int(block)

    if arg is not None:

        try:
            pool_index = int(arg)
            arg_type = 'pool_index'
        except Exception:
            token = arg
            arg_type = 'token'

        if arg_type == 'pool_index':
            await async_print_fuse_pool_summary(
                pool_index=pool_index, block=block_number
            )
        elif arg_type == 'token':
            await async_print_fuse_token_summary(token, block_number)

    else:
        await async_print_all_fuse_pools_summary(block=block_number)


async def async_print_fuse_pool_summary(
    pool_index: int, block: spec.BlockNumberReference
) -> None:
    all_pools = await rari_utils.async_get_all_pools(block=block)
    pool = all_pools[pool_index]
    comptroller = pool[2]
    standard_block = evm.standardize_block_number(block)
    block_data = await rpc.async_eth_get_block_by_number(
        block_number=standard_block,
        include_full_transactions=False,
    )

    tokens_data = await rari_utils.async_get_pool_summary(
        comptroller=comptroller,
        block=block,
    )
    pool_name = await rari_utils.async_get_pool_name(comptroller=comptroller)
    rari_utils.print_fuse_pool_summary(
        block=block_data,
        tokens_data=tokens_data,
        pool_name=pool_name,
        comptroller=comptroller,
    )


async def async_print_all_fuse_pools_summary(
    block: spec.BlockNumberReference,
) -> None:

    await rari_utils.async_print_all_pool_summary(block=block)


async def async_print_fuse_token_summary(
    token: spec.Address,
    block: spec.BlockNumberReference,
) -> None:
    if token == 'ETH':
        token = '0x0000000000000000000000000000000000000000'
    await rari_utils.async_print_fuse_token_summary(token=token, block=block)
