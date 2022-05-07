from __future__ import annotations

import typing

import toolsql

from ctc import spec


async def async_store_block(
    block: spec.Block,
    conn: toolsql.SAConnection,
) -> None:
    raise NotImplementedError()


async def async_store_blocks(
    blocks: typing.Sequence[spec.Block],
    conn: toolsql.SAConnection,
) -> None:
    raise NotImplementedError()


async def async_query_block(
    block: int | str,
    conn: toolsql.SAConnection,
) -> spec.Block | None:
    raise NotImplementedError()


async def async_query_blocks(
    blocks: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.SAConnection,
) -> typing.Sequence[spec.Block | None]:
    raise NotImplementedError()


async def async_delete_block(
    block: int | str,
    conn: toolsql.SAConnection,
) -> None:
    raise NotImplementedError()


async def async_delete_blocks(
    blocks: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.SAConnection,
) -> None:
    raise NotImplementedError()
