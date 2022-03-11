from ctc import binary


def get_command_spec():
    return {
        'f': keccack_command,
        'help': 'compute keccak hash of data\n\nby default, data treated as hex if it starts with "0x", or treated as text otherwise',
        'args': [
            {'name': 'data', 'help': 'data to hash'},
            {
                'name': '--text',
                'action': 'store_true',
                'help': 'treat input data as text instead of hex',
            },
            {
                'name': '--hex',
                'action': 'store_true',
                'help': 'treat data as hex',
            },
            {
                'name': '--raw',
                'action': 'store_true',
                'help': 'omit "0x" prefix on output',
            },
        ],
    }


def keccack_command(data, text, hex, raw):
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

    if raw:
        if not keccak.startswith('0x'):
            raise Exception('wrong format')
        keccak = keccak[2:]

    print(keccak)

