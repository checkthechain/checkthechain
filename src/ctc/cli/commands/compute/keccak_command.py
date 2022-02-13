from ctc import binary


def get_command_spec():
    return {
        'f': keccack_command,
        'args': [
            {'name': 'data'},
            {'name': '--text', 'kwargs': {'action': 'store_true'}},
            {'name': '--hex', 'kwargs': {'action': 'store_true'}},
        ],
    }


def keccack_command(data, text, hex):
    if text:
        hex = False
    elif hex:
        pass
    else:
        hex = data.startswith('0x')

    if hex:
        keccak = binary.keccak(data)
    else:
        keccak = binary.keccak_text(data)
    print(keccak)

