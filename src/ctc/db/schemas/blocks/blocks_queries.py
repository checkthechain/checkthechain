from __future__ import annotations

import typing

from ctc import spec

from ... import connect_utils
from . import blocks_statements


async def async_query_block(
    block_number: int,
    network: spec.NetworkReference,
) -> spec.Block | None:
    engine = connect_utils.create_engine(
        schema_name='blocks',
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await blocks_statements.async_select_block(
            block_number=block_number,
            conn=conn,
            network=network,
        )


async def async_query_blocks(
    block_numbers: typing.Sequence[int],
    network: spec.NetworkReference,
) -> typing.Sequence[spec.Block | None]:
    engine = connect_utils.create_engine(
        schema_name='blocks',
        network=network,
    )
    if engine is None:
        return [None] * len(block_numbers)
    with engine.connect() as conn:
        return await blocks_statements.async_select_blocks(
            block_numbers=block_numbers,
            conn=conn,
            network=network,
        )


# async_query_blocks = with_connection(
#     blocks_statements.async_select_blocks,
#     'blocks',
#     # ['block_numbers'],
# )
