from __future__ import annotations

import toolcli


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': root_command,
        'help': 'cli interface to ctc and its subcommands',
        'args': [
            {
                'name': 'query',
                'nargs': '*',
                'help': 'address, block number, tx hash, or ERC20 symbol',
            }
        ],
        'examples': [
            '0x3a44deb6159843a584cf6ede188cd9f4161dc215',
            '14000000',
            '0xf48e1d4211c1df4cbf19aa0e99741ce0ad371a9906725bb60829147e763ffdf9',
            'DAI',
        ],
        'extra_data': ['parse_spec'],
    }


def root_command(query: str, parse_spec: toolcli.ParseSpec) -> None:

    execute_other_command_sequence = (
        toolcli.command_utils.execution.execute_other_command_sequence
    )

    if len(query) == 0:
        execute_other_command_sequence(
            command_sequence=('help',),
            args={'parse_spec': parse_spec},
            parse_spec=parse_spec,
        )
    elif len(query) == 1:
        item = query[0]
        if len(item) <= 9 and str.isnumeric(item):
            # treat as block number
            block = int(item)
            execute_other_command_sequence(
                command_sequence=('block',),
                args={'parse_spec': parse_spec, 'block': block},
                parse_spec=parse_spec,
            )

        elif item.startswith('0x') and len(item) == 66:
            # treat as transaction hash
            transaction = item
            execute_other_command_sequence(
                command_sequence=('tx',),
                args={'parse_spec': parse_spec, 'transaction': transaction},
                parse_spec=parse_spec,
            )

        elif (item.startswith('0x') and len(item) == 42) or item.endswith(
            '.eth'
        ):
            # treat as address
            address = item
            execute_other_command_sequence(
                command_sequence=('address',),
                args={'parse_spec': parse_spec, 'address': address},
                parse_spec=parse_spec,
            )

        elif str.isalnum(item) and len(item) <= 20:
            try:
                execute_other_command_sequence(
                    command_sequence=('symbol',),
                    args={'parse_spec': parse_spec, 'query': item},
                    parse_spec=parse_spec,
                )
            except LookupError:
                execute_other_command_sequence(
                    command_sequence=('help',),
                    args={'parse_spec': parse_spec},
                    parse_spec=parse_spec,
                )

        else:
            raise Exception('unknown query: ' + str(query))
    else:
        raise Exception('unknown query: ' + str(query))
