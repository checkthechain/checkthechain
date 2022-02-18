from ctc import binary


def get_command_spec():
    return {
        'f': hex_command,
        'args': [
            {'name': 'data'},
            {'name': '--raw', 'kwargs': {'action': 'store_true'}},
        ],
    }


def hex_command(data, raw):
    if raw:
        output = binary.ascii_to_raw_hex(data)
    else:
        output = binary.ascii_to_prefix_hex(data)
    print(output)

