from __future__ import annotations

import typing

from ctc import evm
from ctc import spec


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


async def async_resolve_block_range(
    block_range: typing.Union[str, typing.Sequence[str], spec.BlockRange],
    provider: spec.ProviderReference = None,
) -> tuple[int, int]:
    from ctc import evm

    if not isinstance(block_range, dict):
        parsed_range = parse_str_block_range(block_range)
    else:
        parsed_range = block_range

    start_block, end_block = await evm.async_block_numbers_to_int(
        [parsed_range['start_block'], parsed_range['end_block']],
        provider=provider,
    )

    if parsed_range['open_start']:
        start_block = start_block + 1
    if parsed_range['open_end']:
        end_block = end_block - 1

    if start_block > end_block:
        raise Exception('invalid block range: ' + str([start_block, end_block]))

    return start_block, end_block


async def async_resolve_block_sample(
    block_sample: typing.Union[str, typing.Sequence[str], spec.BlockSample],
    provider: spec.ProviderReference = None,
) -> list[int]:
    from ctc import evm

    if not isinstance(block_sample, dict):
        block_sample = parse_block_sample(block_sample)

    start_block, end_block = await evm.async_block_numbers_to_int(
        [block_sample['start_block'], block_sample['end_block']],
        provider=provider,
    )

    if block_sample['open_start']:
        start_block = start_block + 1
    if block_sample['open_end']:
        end_block = end_block - 1

    if start_block > end_block:
        raise Exception('invalid block range: ' + str([start_block, end_block]))

    block_interval = block_sample['block_interval']
    if block_interval is None:
        block_interval = 1
    return list(range(start_block, end_block + 1, block_interval))


def is_block_range(block_spec: typing.Union[str, typing.Sequence[str]]) -> bool:
    try:
        parse_str_block_range(block_spec)
        return True
    except ValueError:
        return False


def is_block_sample(
    block_spec: typing.Union[str, typing.Sequence[str]]
) -> bool:
    try:
        parse_block_sample(block_spec)
        return True
    except ValueError:
        return False


def parse_str_block_range(
    block_spec: typing.Union[str, typing.Sequence[str]]
) -> spec.BlockRange:
    """
    ## Example: All of the following should produce the same output
    - "[123 456]"
    - "[123,456]"
    - "[123, 456]"
    - "[123 , 456]"
    - "[123 ,456]"
    - "[123  456]"
    - "[123,  456]"
    - "[123  ,  456]"
    - "[123  ,456]"
    - "[ 123 456]"
    - "[ 123,456   ]"
    - "[ 123, 456]"
    - "[ 123 , 456]"
    - "[ 123 ,456]"
    - "123:456"
    """

    from ctc import binary

    tokens = tokenize(block_spec)

    # parse out the four components
    if len(tokens) != 4:
        raise ValueError(
            'invalid block range specification: ' + str(block_spec)
        )
    start_type, start_block_str, end_block_str, end_type = tokens

    # convert to int if applicable
    if start_block_str in ['latest', 'earliest', 'pending']:
        start_block: spec.StandardBlockNumber = start_block_str  # type: ignore
    else:
        start_block = binary.raw_block_number_to_int(start_block_str)
    if end_block_str in ['latest', 'earliest', 'pending']:
        end_block: spec.StandardBlockNumber = end_block_str  # type: ignore
    else:
        end_block = binary.raw_block_number_to_int(end_block_str)

    # detect interval types
    if start_type == '(':
        open_start = True
    elif start_type == '[':
        open_start = False
    else:
        raise ValueError(
            'invalid interval type in block range: ' + str(block_spec)
        )
    if start_type == '(':
        open_end = True
    elif start_type == '[':
        open_end = False
    else:
        raise ValueError(
            'invalid interval type in block range: ' + str(block_spec)
        )

    return {
        'start_block': start_block,
        'end_block': end_block,
        'open_start': open_start,
        'open_end': open_end,
    }


def parse_block_sample(
    block_spec: typing.Union[str, typing.Sequence[str]]
) -> spec.BlockSample:

    from ctc import binary

    tokens = tokenize(block_spec)

    # parse out the four components
    if len(tokens) == 4:
        start_type, start_block_str, end_block_str, end_type = tokens
        block_interval_str = None
    elif len(tokens) == 5:
        (
            start_type,
            start_block_str,
            end_block_str,
            block_interval_str,
            end_type,
        ) = tokens
    else:
        raise ValueError(
            'invalid block range specification: ' + str(block_spec)
        )

    # convert to int if applicable
    if start_block_str in spec.block_number_names:
        if typing.TYPE_CHECKING:
            start_block_str = typing.cast(spec.BlockNumberName, start_block_str)
        start_block: spec.StandardBlockNumber = start_block_str
    else:
        start_block = binary.raw_block_number_to_int(start_block_str)
    if end_block_str in spec.block_number_names:
        if typing.TYPE_CHECKING:
            end_block_str = typing.cast(spec.BlockNumberName, end_block_str)
        end_block: spec.StandardBlockNumber = end_block_str
    else:
        end_block = binary.raw_block_number_to_int(end_block_str)
    if block_interval_str is not None:
        block_interval = binary.raw_block_number_to_int(block_interval_str)
    else:
        block_interval = None

    # detect interval types
    if start_type == '(':
        open_start = True
    elif start_type == '[':
        open_start = False
    else:
        raise ValueError(
            'invalid interval type in block range: ' + str(block_spec)
        )
    if end_type == ')':
        open_end = True
    elif end_type == ']':
        open_end = False
    else:
        raise ValueError(
            'invalid interval type in block range: ' + str(block_spec)
        )

    return {
        'start_block': start_block,
        'end_block': end_block,
        'block_interval': block_interval,
        'open_start': open_start,
        'open_end': open_end,
    }


def tokenize(data: typing.Union[str, typing.Sequence[str]]) -> list[str]:
    """break up string into tokens, tokens can be separated by commas or spaces

    creates separate tokens for:
    - "(" or "[" at beginning
    - ")" or "]" at end
    """

    if isinstance(data, str) and ':' in data:
        return ['['] + data.split(':') + [']']
    elif len(data) == 1 and isinstance(data[0], str) and ':' in data[0]:
        return ['['] + data[0].split(':') + [']']

    # break into tokens
    if isinstance(data, str):
        data = [data]
    tokens = []
    for datum in data:
        datum = datum.replace(',', ' ')
        subtokens = datum.split(' ')

        for token in subtokens:
            if len(token) == 0:
                continue
            elif len(token) == 1:
                tokens.append(token)
            else:

                start_interval = token[0] in ['(', '[']
                end_interval = token[-1] in [')', ']']

                # convert token based on contained intervals
                if start_interval and end_interval:
                    tokens.append(token[0])
                    if len(token) > 2:
                        tokens.append(token[1:-1])
                    tokens.append(token[-1])
                elif start_interval:
                    tokens.append(token[0])
                    tokens.append(token[1:])
                elif end_interval:
                    tokens.append(token[:-1])
                    tokens.append(token[-1])
                else:
                    tokens.append(token)

    return tokens
