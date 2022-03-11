from ctc import evm


def get_command_spec():
    return {
        'f': checksum_command,
        'help': 'compute checksum of address',
        'args': [
            {'name': 'address', 'help': 'address to get checksum of'},
        ],
    }


def checksum_command(address):
    print(evm.get_address_checksum(address))

