from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import directory


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_find_command,
        'help': 'search for item in directory',
        'args': [
            {'name': 'query', 'help': 'ERC20 symbol'},
        ],
        'examples': [
            'FEI',
        ],
    }


async def async_find_command(query: str) -> None:
    try:
        result = directory.get_erc20_metadata(symbol=query)
        row = []
        labels: typing.Sequence[
            typing.Literal['symbol', 'decimals', 'address']
        ] = ['symbol', 'decimals', 'address']
        for key in labels:
            row.append(result[key])
        rows = [row]
        toolstr.print_table(rows=rows, labels=labels)
    except LookupError:
        print('could not find anything')
