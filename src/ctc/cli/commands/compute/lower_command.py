
def get_command_spec():
    return {
        'f': lower_command,
        'help': 'convert to lower case',
        'args': [
            {'name': 'arg'},
        ],
    }


def lower_command(arg):
    print(arg.lower())

