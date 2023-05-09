from __future__ import annotations

import typing

from ctc import evm
from ctc import spec


def parse_network(network: str) -> spec.NetworkReference:
    if network.isnumeric():
        return int(network)
    else:
        return network


async def async_parse_block(
    block: str, context: spec.Context = None
) -> spec.BlockNumberReference:
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
    context: spec.Context = None,
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
        start_block = await _async_resolve_single_block(
            raw_start_block, context=context
        )

    if raw_end_block == '':
        end_block = default_end
    else:
        end_block = await _async_resolve_single_block(
            raw_end_block, context=context
        )

    return start_block, end_block


async def async_parse_block_chunks(
    text: str,
    *,
    default_interval: int | None = None,
    context: spec.Context = None,
) -> tuple[int, int, int]:
    """

    Examples
    14_000_000:14_000_100:10
    14M:14.1M:1K
    10:100:50
    14M:latest:500k
    """
    if text.count(':') == 2:
        start_block, end_block, interval = text.split(':')
    elif text.count(':') == 1:
        start_block, end_block = text.split(':')
        interval = None
    else:
        raise Exception(
            'block chunks must be specified as start_block:end_block:chunk_size'
        )
    start_block_int = await _async_resolve_single_block(
        start_block, context=context
    )
    end_block_int = await _async_resolve_single_block(
        end_block, context=context
    )
    if interval is not None:
        interval_int = await _async_resolve_single_block(
            interval, context=context
        )
    else:
        if default_interval is None:
            raise Exception('must specify default_interval')
        interval_int = default_interval
    return start_block_int, end_block_int, interval_int


def sync_parse_block_chunks(
    text: str,
    *,
    default_interval: int | None = None,
    context: spec.Context = None,
) -> tuple[int, int, int]:
    """

    Examples
    14_000_000:14_000_100:10
    14M:14.1M:1K
    10:100:50
    14M:latest:500k
    """
    if text.count(':') == 2:
        start_block, end_block, interval = text.split(':')
    elif text.count(':') == 1:
        start_block, end_block = text.split(':')
        interval = None
    else:
        raise Exception(
            'block chunks must be specified as start_block:end_block:chunk_size'
        )
    start_block_int = _sync_resolve_single_block(start_block, context=context)
    end_block_int = _sync_resolve_single_block(end_block, context=context)
    if interval is not None:
        interval_int = _sync_resolve_single_block(interval, context=context)
    else:
        if default_interval is None:
            raise Exception('must specify default_interval')
        interval_int = default_interval
    return start_block_int, end_block_int, interval_int


async def async_parse_block_slice(
    text: str | typing.Sequence[str],
    n: int | None = None,
    *,
    context: spec.Context = None,
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
            subblocks = await async_parse_block_slice(
                subtext, n=n, context=context
            )
            blocks.extend(subblocks)
        return blocks

    elif isinstance(text, str):
        # single block
        if text == 'latest':
            return [await evm.async_get_latest_block_number(context=context)]

        elif text.isnumeric():
            return [int(text)]

        # list of blocks
        elif ' ' in text:
            pieces = text.split(' ')
            blocks = []
            for piece in pieces:
                block = await _async_resolve_single_block(
                    piece, context=context
                )
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
                start_block = await _async_resolve_single_block(
                    raw_start_block, context=context
                )
                diff = await _async_resolve_single_block(
                    raw_end_block, context=context
                )
                end_block = start_block + diff
                if raw_end_block[0] == '-':
                    start_block, end_block = end_block, start_block
            else:
                start_block = await _async_resolve_single_block(
                    raw_start_block, context=context
                )
                end_block = await _async_resolve_single_block(
                    raw_end_block, context=context
                )

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


async def _async_resolve_single_block(
    text: str,
    context: spec.Context = None,
) -> int:
    chars = set(text)
    numbers = set('0123456789')

    if chars.issubset(numbers):
        return int(text)
    elif chars.issubset(numbers | {'_'}):
        import ast

        result: int = ast.literal_eval(text)
        return result
    elif len(text) > 1 and set(text[:-1]).issubset(numbers):
        if text[-1].lower() == 'b':
            factor = 1_000_000_000
        elif text[-1].lower() == 'm':
            factor = 1_000_000
        elif text[-1].lower() == 'k':
            factor = 1_000
        else:
            raise Exception('unknown suffix')
        return int(text[:-1]) * factor
    elif text == 'latest':
        return await evm.async_get_latest_block_number(context=context)
    else:
        # scentific notation
        try:
            as_float = float(text)
            as_int = int(as_float)
            if abs(as_float - as_int) > 0.00000001:
                raise Exception('must specify integer block values')
            return as_int
        except ValueError:
            raise Exception('could not parse block: ' + str(text))


def _sync_resolve_single_block(
    text: str,
    context: spec.Context = None,
) -> int:
    chars = set(text)
    numbers = set('0123456789')

    if chars.issubset(numbers):
        return int(text)
    elif chars.issubset(numbers | {'_'}):
        import ast

        result: int = ast.literal_eval(text)
        return result
    elif len(text) > 1 and set(text[:-1]).issubset(numbers):
        if text[-1].lower() == 'b':
            factor = 1_000_000_000
        elif text[-1].lower() == 'm':
            factor = 1_000_000
        elif text[-1].lower() == 'k':
            factor = 1_000
        else:
            raise Exception('unknown suffix')
        return int(text[:-1]) * factor
    elif text == 'latest':
        return evm.sync_get_latest_block_number(context=context)
    else:
        # scentific notation
        try:
            as_float = float(text)
            as_int = int(as_float)
            if abs(as_float - as_int) > 0.00000001:
                raise Exception('must specify integer block values')
            return as_int
        except ValueError:
            raise Exception('could not parse block: ' + str(text))

