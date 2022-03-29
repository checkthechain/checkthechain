from __future__ import annotations

import typing

from ctc import spec


def set_block(block: spec.Block) -> None:
    pass


def set_blocks(blocks: typing.Sequence[spec.Block]) -> None:
    pass


def get_block(
    block_number: int | None = None, block_hash: str | None = None
) -> spec.Block:
    pass


def get_blocks(
    block_numbers: typing.Sequence[int] | None = None,
    start_block_number: int | None = None,
    end_block_number: int | None = None,
    block_hashes: typing.Sequence[str] | None = None,
    start_block_hash: str | None = None,
    end_block_hash: str | None = None,
) -> spec.Block:
    pass


def delete_block(
    block_number: int | None = None, block_hash: str | None = None
) -> None:
    pass


def delete_blocks(
    block_numbers: typing.Sequence[int] | None = None,
    start_block_number: int | None = None,
    end_block_number: int | None = None,
    block_hashes: typing.Sequence[str] | None = None,
    start_block_hash: str | None = None,
    end_block_hash: str | None = None,
) -> None:
    pass

