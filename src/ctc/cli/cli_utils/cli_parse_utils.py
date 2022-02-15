from __future__ import annotations

import typing

from ctc import evm
from ctc import spec


async def async_resolve_block_range(
    block_range: typing.Union[str, typing.Sequence[str], spec.BlockRange],
) -> tuple[int, int]:

    if not isinstance(block_range, dict):
        block_range = parse_block_range(block_range)

    start_block, end_block = await evm.async_block_numbers_to_int(
        [block_range['start_block'], block_range['end_block']],
    )

    if block_range['open_start']:
        start_block = start_block + 1
    if block_range['open_end']:
        end_block = end_block - 1

    if start_block > end_block:
        raise Exception('invalid block range: ' + str([start_block, end_block]))

    return start_block, end_block


async def async_resolve_block_sample(
    block_sample: typing.Union[str, typing.Sequence[str], spec.BlockSample],
) -> list[int]:

    if not isinstance(block_sample, dict):
        block_sample = parse_block_sample(block_sample)

    start_block, end_block = await evm.async_block_numbers_to_int(
        [block_sample['start_block'], block_sample['end_block']],
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
        parse_block_range(block_spec)
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


def parse_block_range(
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
    """

    tokens = tokenize(block_spec)

    # parse out the four components
    if len(tokens) != 4:
        raise ValueError(
            'invalid block range specification: ' + str(block_spec)
        )
    start_type, start_block, end_block, end_type = tokens

    # convert to int if applicable
    if start_block not in spec.block_number_names:
        start_block = evm.raw_block_number_to_int(start_block)
    if end_block not in spec.block_number_names:
        end_block = evm.raw_block_number_to_int(end_block)

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


def parse_block_sample(block_spec):

    tokens = tokenize(block_spec)

    # parse out the four components
    if len(tokens) == 4:
        start_type, start_block, end_block, end_type = tokens
        block_interval = None
    elif len(tokens) == 5:
        start_type, start_block, end_block, block_interval, end_type = tokens
    else:
        raise ValueError(
            'invalid block range specification: ' + str(block_spec)
        )

    # convert to int if applicable
    if start_block not in spec.block_number_names:
        start_block = evm.raw_block_number_to_int(start_block)
    if end_block not in spec.block_number_names:
        end_block = evm.raw_block_number_to_int(end_block)
    if block_interval is not None:
        block_interval = evm.raw_block_number_to_int(block_interval)

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

