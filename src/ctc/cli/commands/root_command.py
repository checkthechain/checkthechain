import toolcli


def get_command_spec():
    return {
        'f': root_command,
        'args': [
            {'name': ['-h', '--help'], 'help': 'print help message', 'action': 'store_true'},
        ],
        'special': {
            'include_parse_spec': True,
        },
    }


def root_command(parse_spec, help):
    toolcli.execute_other_command_sequence(
        command_sequence=('help',),
        args=[],
        parse_spec=parse_spec,
    )

