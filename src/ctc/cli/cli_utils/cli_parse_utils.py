from __future__ import annotations

import typing

from ctc import evm
from ctc import spec


def parse_network(network: str) -> spec.NetworkReference:
    if network.isnumeric():
        return int(network)
    else:
        return network


async def async_parse_block(block: str) -> spec.BlockNumberReference:
    if block.isnumeric():
        return int(block)
    elif block == 'latest':
        return block
    else:
        raise Exception('unknown block format: ' + str(block))


async def async_parse_block_range(
    text: str,
    *,
    default_start: int | None = None,
    default_end: int | None = None,
) -> tuple[int | None, int | None]:
    """convert a cli block range to its start and end bounds

    Example block slices
        16000:        -->   (16000, None)
        :16010        -->   (None, 16010)
        16000:16010   -->   (16000, 16010)
        14e6:15e6     -->   (14000000, 15000000)
    """

    if text.count(':') != 1:
        raise Exception('range must have format: [start_block]:[end_block]')

    raw_start_block, raw_end_block = text.split(':')

    if raw_start_block == '':
        start_block = default_start
    else:
        start_block = await _async_resolve_single_block(raw_start_block)

    if raw_end_block == '':
        end_block = default_end
    else:
        end_block = await _async_resolve_single_block(raw_end_block)

    return start_block, end_block


async def async_parse_block_slice(
    text: str | typing.Sequence[str],
    n: int | None = None,
) -> typing.Sequence[int]:
    """convert a cli block slice to a list of integer block numbers

    Example block slices
        16000
        16000 16010 16020 16030
        16010:16030:10
        16010:16030
        15000000:latest:100000
        16010:+20
        16030:-20
        latest:-20:2
        14e6:15e6
        14e6:15e6:1e5
    """

    # list of blocks
    if isinstance(text, (list, tuple)):

        blocks: list[int] = []
        for subtext in text:
            subblocks = await async_parse_block_slice(subtext, n=n)
            blocks.extend(subblocks)
        return blocks

    elif isinstance(text, str):

        # single block
        if text == 'latest':
            return [await evm.async_get_latest_block_number()]

        elif text.isnumeric():
            return [int(text)]

        # list of blocks
        elif ' ' in text:
            pieces = text.split(' ')
            blocks = []
            for piece in pieces:
                block = await _async_resolve_single_block(piece)
                blocks.append(block)
            return blocks

        # block slice
        elif ':' in text:
            pieces = text.split(':')

            if len(pieces) == 2:
                raw_start_block = pieces[0]
                raw_end_block = pieces[1]
                interval: int | None = None
            elif len(pieces) == 3:
                raw_start_block = pieces[0]
                raw_end_block = pieces[1]
                interval = int(pieces[2])
            else:
                raise Exception('invalid block slice specification')

            if raw_end_block[0] in ['+', '-']:
                start_block = await _async_resolve_single_block(raw_start_block)
                diff = await _async_resolve_single_block(raw_end_block)
                end_block = start_block + diff
                if raw_end_block[0] == '-':
                    start_block, end_block = end_block, start_block
            else:
                start_block = await _async_resolve_single_block(raw_start_block)
                end_block = await _async_resolve_single_block(raw_end_block)

            if end_block < start_block:
                raise Exception('invalid block slice specification')

            if interval is None:
                if n is None:
                    interval = 1
                else:
                    interval = int((end_block - start_block) / n)

            blocks = list(range(start_block, end_block + 1, interval))
            if blocks[-1] != end_block:
                blocks.append(end_block)

            return blocks

    raise Exception('invalid block slice specification')


async def _async_resolve_single_block(text: str) -> int:
    if text.isnumeric():
        return int(text)
    elif text == 'latest':
        return await evm.async_get_latest_block_number()
    else:
        try:
            as_float = float(text)
            as_int = int(as_float)
            if abs(as_float - as_int) > 0.00000001:
                raise Exception('must specify integer block values')
            return as_int
        except ValueError:
            raise Exception('could not parse block: ' + str(text))
