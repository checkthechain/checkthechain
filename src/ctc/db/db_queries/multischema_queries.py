from __future__ import annotations

import typing
from typing_extensions import Literal

from ctc import spec

from .. import db_connect
from .. import db_statements
from .. import db_management


async def async_query_timestamp_block(
    timestamp: int,
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> int | None:

    timestamp_schema = db_management.get_active_timestamp_schema()
    if timestamp_schema is None:
        return None
    engine = db_connect.create_engine(
        datatype=timestamp_schema,
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await db_statements.async_select_timestamp_block(
            timestamp=timestamp,
            mode=mode,
            network=network,
            conn=conn,
        )


async def async_query_block_timestamp(
    block_number: int,
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = db_management.get_active_timestamp_schema()
    if timestamp_schema is None:
        return None
    engine = db_connect.create_engine(
        datatype=timestamp_schema,
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await db_statements.async_select_block_timestamp(
            block_number=block_number,
            network=network,
            conn=conn,
        )


async def async_query_max_block_number(
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = db_management.get_active_timestamp_schema()
    if timestamp_schema is None:
        return None
    engine = db_connect.create_engine(
        datatype=timestamp_schema,
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await db_statements.async_select_max_block_number(
            network=network,
            conn=conn,
        )


async def async_query_max_block_timestamp(
    network: spec.NetworkReference | None = None,
) -> int | None:

    timestamp_schema = db_management.get_active_timestamp_schema()
    if timestamp_schema is None:
        return None
    engine = db_connect.create_engine(
        datatype=timestamp_schema,
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await db_statements.async_select_max_block_timestamp(
            network=network,
            conn=conn,
        )


async def async_query_timestamps_blocks(
    timestamps: typing.Sequence[int],
    network: spec.NetworkReference | None = None,
    mode: Literal['before', 'after', 'equal'] = 'after',
) -> typing.Sequence[int | None]:

    timestamp_schema = db_management.get_active_timestamp_schema()
    if timestamp_schema is None:
        return [None] * len(timestamps)
    engine = db_connect.create_engine(
        datatype=timestamp_schema,
        network=network,
    )
    if engine is None:
        return [None] * len(timestamps)
    with engine.connect() as conn:
        return await db_statements.async_select_timestamps_blocks(
            timestamps=timestamps,
            network=network,
            mode=mode,
            conn=conn,
        )


async def async_query_block_timestamps(
    block_numbers: typing.Sequence[typing.SupportsInt],
    network: spec.NetworkReference | None = None,
) -> typing.Sequence[int | None]:

    timestamp_schema = db_management.get_active_timestamp_schema()
    if timestamp_schema is None:
        return [None] * len(block_numbers)
    engine = db_connect.create_engine(
        datatype=timestamp_schema,
        network=network,
    )
    if engine is None:
        return [None] * len(block_numbers)
    with engine.connect() as conn:
        return await db_statements.async_select_block_timestamps(
            block_numbers=block_numbers,
            network=network,
            conn=conn,
        )
