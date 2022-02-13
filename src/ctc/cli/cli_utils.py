from __future__ import annotations

import os
import typing

import toolcli

from ctc import evm


async def async_resolve_blocks(
    block_spec: typing.Union[str, list[str]]
) -> list[int]:

    # convert to tokens
    if isinstance(block_spec, str):
        tokens = [block_spec]
    else:
        tokens = [
            subtoken
            for token in block_spec
            for subtoken in token.strip(',').split(',')
        ]

    if len(tokens) == 0:
        raise Exception('invalid block specification: ' + str(block_spec))

    start_range = tokens[0][0] in ['[', '(']
    end_range = tokens[-1][-1] in [']', ')']

    if (start_range and not end_range) or (not start_range and end_range):
        raise Exception('invalid block specification: ' + str(block_spec))

    if start_range and end_range:

        open_start = tokens[0][0] == '('
        open_end = tokens[-1][-1] == ')'
        stripped = [token.strip('()[] \t') for token in tokens]

        if len(tokens) == 1:
            if open_start or open_end:
                raise Exception(
                    'invalid block specification: ' + str(block_spec)
                )
            blocks = [stripped[0]]

        else:
            start_block, end_block = await evm.async_block_numbers_to_int(
                stripped[:2]
            )
            if not open_start:
                start_block += 1

            if len(tokens) == 2:
                blocks = list(range(start_block, end_block))
            elif len(tokens) == 3:
                block_interval = int(stripped[2])
                blocks = list(range(start_block, end_block, block_interval))
            else:
                raise Exception(
                    'invalid block specification: ' + str(block_spec)
                )

            if not open_end:
                blocks.append(end_block)

            else:
                raise Exception(
                    'invalid block specification: ' + str(block_spec)
                )

    else:
        blocks = tokens

    return await evm.async_block_numbers_to_int(blocks=blocks)


async def async_resolve_block_range(block_spec):
    """
    [123 456]
    [123,456]
    [123, 456]
    [123 , 456]
    [123 ,456]
    [123  456]
    [123,  456]
    [123  ,  456]
    [123  ,456]
    [ 123 456]
    [ 123,456]
    [ 123, 456]
    [ 123 , 456]
    [ 123 ,456]
    """

    if isinstance(block_spec, str):
        block_spec = [block_spec]

    # parse tokens
    tokens = [subtoken for token in block_spec for subtoken in token.split(',')]
    tokens = [subtoken for token in tokens for subtoken in token.split(' ')]
    tokens = [token.strip('()[]') for token in tokens]
    tokens = [token for token in tokens if token != '']
    if len(tokens) != 2:
        raise Exception(
            'invalid specification for block range: ' + str(block_spec)
        )

    # standardize
    start_block, end_block = await evm.async_block_numbers_to_int(tokens)

    # check for open bounds
    open_start = tokens[0][0] == '('
    open_end = tokens[-1][-1] == ')'
    if open_start:
        start_block += 1
    if open_end:
        end_block -= 1

    if start_block > end_block:
        raise Exception(
            'invalid specification for block range: ' + str(block_spec)
        )

    return start_block, end_block


def output_data(data, output, overwrite):

    if output == 'stdout':
        # print(data)
        import tooltable
        import toolstr

        rows = []
        for index, values in data.iterrows():
            row = []
            row.append(index)
            for value in values.values:
                if value and not isinstance(value, str):
                    value = toolstr.format(value)
                row.append(value)
            rows.append(row)
        columns = [data.index.name] + list(data.columns)
        tooltable.print_table(rows=rows, headers=columns)

    else:

        # check whether file exists
        if os.path.isfile(output):
            if overwrite:
                pass
            elif toolcli.input_yes_or_no('File already exists. Overwrite? '):
                pass
            else:
                raise Exception('aborting')

        if output.endswith('.csv'):
            data.to_csv(output)

        elif output.endswith('.json'):
            data.to_json(output)

        else:
            raise Exception('unknown output format: ' + str(output))

