import toolcli


def get_command_spec():
    return {
        'f': root_command,
        'special': {
            'parse_spec': True,
        },
    }


def root_command(parse_spec):
    toolcli.execute_other_command_sequence(
        command_sequence=('help',),
        parse_spec=parse_spec,
    )

