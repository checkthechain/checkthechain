from ctc import binary


def get_command_spec():
    return {
        'f': ascii_command,
        'args': [
            {'name': 'data'},
        ],
    }


def ascii_command(data):
    ascii = binary.hex_to_ascii(data)
    print(ascii)

