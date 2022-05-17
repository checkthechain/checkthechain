from __future__ import annotations

import typing

import toolsql

from ctc import spec


async def async_upsert_block(
    block: spec.Block,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    raise NotImplementedError()


async def async_upsert_blocks(
    blocks: typing.Sequence[spec.Block],
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    raise NotImplementedError()


async def async_select_block(
    block_number: int | str,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> spec.Block | None:
    raise NotImplementedError()


async def async_select_blocks(
    block_numbers: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> typing.Sequence[spec.Block | None]:
    raise NotImplementedError()


async def async_delete_block(
    block_number: int | str,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    raise NotImplementedError()


async def async_delete_blocks(
    block_nubmers: typing.Sequence[int | str] | None = None,
    *,
    start_block: int | None = None,
    end_block: int | None = None,
    conn: toolsql.SAConnection,
    network: spec.NetworkReference,
) -> None:
    raise NotImplementedError()
