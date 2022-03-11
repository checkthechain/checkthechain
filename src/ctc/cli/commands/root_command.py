import toolcli


def get_command_spec():
    return {
        'f': root_command,
        'help': 'cli interface to ctc and its subcommands',
        'special': {
            'include_parse_spec': True,
        },
    }


def root_command(parse_spec):
    toolcli.execute_other_command_sequence(
        command_sequence=('help',),
        args={'parse_spec': parse_spec},
        parse_spec=parse_spec,
    )

