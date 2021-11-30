
def get_command_spec():
    return {
        'f': root_command,
        'args': [
            {'name': 'args', 'kwargs': {'nargs': '*'}},
        ],
    }


def root_command(args):
    print('args:', args)

