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
        'extra_data': ['parse_spec'],
    }


def root_command(query: str, parse_spec: toolcli.ParseSpec) -> None:
    if len(query) == 0:
        toolcli.execute_other_command_sequence(
            command_sequence=('help',),
            args={'parse_spec': parse_spec},
            parse_spec=parse_spec,
        )
    elif len(query) == 1:
        item = query[0]
        if len(item) <= 9 and str.isnumeric(item):
            # treat as block number
            block = int(item)
            toolcli.execute_other_command_sequence(
                command_sequence=('block',),
                args={'parse_spec': parse_spec, 'block': block},
                parse_spec=parse_spec,
            )

        elif item.startswith('0x') and len(item) == 66:
            # treat as transaction hash
            transaction = item
            toolcli.execute_other_command_sequence(
                command_sequence=('transaction',),
                args={'parse_spec': parse_spec, 'transaction': transaction},
                parse_spec=parse_spec,
            )

        elif (item.startswith('0x') and len(item) == 42) or item.endswith('.eth'):
            # treat as address
            address = item
            toolcli.execute_other_command_sequence(
                command_sequence=('address',),
                args={'parse_spec': parse_spec, 'address': address},
                parse_spec=parse_spec,
            )

        elif str.isalnum(item) and len(item) <= 20:
            try:
                toolcli.execute_other_command_sequence(
                    command_sequence=('symbol',),
                    args={'parse_spec': parse_spec, 'query': item},
                    parse_spec=parse_spec,
                )
            except LookupError:
                toolcli.execute_other_command_sequence(
                    command_sequence=('help',),
                    args={'parse_spec': parse_spec},
                    parse_spec=parse_spec,
                )

        else:
            raise Exception('unknown query: ' + str(query))
    else:
        raise Exception('unknown query: ' + str(query))
