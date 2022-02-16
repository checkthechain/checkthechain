
def get_command_spec():
    return {
        'f': lower_command,
        'args': [
            {'name': 'arg'},
        ],
    }


def lower_command(arg):
    print(arg.lower())

