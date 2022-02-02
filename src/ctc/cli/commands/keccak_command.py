from ctc import binary


def get_command_spec():
    return {
        'f': keccack_command,
        'args': [
            {'name': 'data'},
            {'name': '--text', 'kwargs': {'action': 'store_true'}},
        ],
    }


def keccack_command(data, text):
    if text:
        keccak = binary.keccak_text(data)
    else:
        keccak = binary.keccak(data)
    print(keccak)

