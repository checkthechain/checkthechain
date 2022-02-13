from . import cli_run


def get_command_spec():
    return {
        'f': root_command,
    }


def root_command():
    print('check the chain')
    print()
    print('usage:')
    print('    ctc <subcommands> [options]')
    print()
    print('available subcommands:')
    for command in cli_run.command_index.keys():
        if command == ():
            continue
        print('   ', ' '.join(command))

