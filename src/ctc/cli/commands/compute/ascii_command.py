from ctc import binary


def get_command_spec():
    return {
        'f': ascii_command,
        'help': 'convert hex to ascii',
        'args': [
            {'name': 'data', 'help': 'hex data to convert'},
        ],
    }


def ascii_command(data):
    ascii = binary.hex_to_ascii(data)
    print(ascii)

