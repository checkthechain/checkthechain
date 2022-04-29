from __future__ import annotations

import typing

import toolcli
import tooltable  # type: ignore

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
        headers: typing.Sequence[
            typing.Literal['symbol', 'decimals', 'address']
        ] = ['symbol', 'decimals', 'address']
        for key in headers:
            row.append(result[key])
        rows = [row]
        tooltable.print_table(rows=rows, headers=headers)
    except LookupError:
        print('could not find anything')

