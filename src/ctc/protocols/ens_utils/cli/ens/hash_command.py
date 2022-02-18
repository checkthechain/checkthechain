from ctc import evm
from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': hash_command,
        'args': [
            {'name': 'name'},
        ]
    }


def hash_command(name):
    print(ens_utils.hash_name(name))

