from __future__ import annotations

import typing

from ctc import spec


async def async_select_block_transactions(
    block_number: int,
    *,
    context: spec.Context,
) -> typing.Sequence[spec.DBTransaction] | None:
    raise NotImplementedError()


async def async_select_blocks_transactions(
    block_numbers: typing.Sequence[int],
    *,
    context: spec.Context,
) -> tuple[typing.Sequence[spec.DBTransaction], typing.Sequence[int]]:
    raise NotImplementedError()

