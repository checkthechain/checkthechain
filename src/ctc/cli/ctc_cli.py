import toolcli


def create_ctc_cli():

    command_indices = toolcli.autoindex_command_root(
        root_module_name='ctc.cli.commands',
    )
    cli = toolcli.BaseCLI(
        command_indices=command_indices,
        passthrough_command=passthrough_command,
    )
    return cli


def passthrough_command(command):

    arg = command[1]

    if len(arg) <= 9 and str.isnumeric(arg):
        return 'block'

    elif arg.startswith('0x') and len(arg) == 66:
        return 'transaction'

    elif arg.startswith('0x') and len(arg) == 42:
        return 'address'

    else:
        raise Exception('could not determine command')

