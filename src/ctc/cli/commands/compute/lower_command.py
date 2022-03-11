
def get_command_spec():
    return {
        'f': lower_command,
        'help': 'convert to lower case',
        'args': [
            {'name': 'text', 'help': 'text to convert'},
        ],
    }


def lower_command(text):
    print(text.lower())

