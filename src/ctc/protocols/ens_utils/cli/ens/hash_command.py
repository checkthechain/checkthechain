from ctc.protocols import ens_utils


def get_command_spec():
    return {
        'f': hash_command,
        'help': 'output hash of ENS name',
        'args': [
            {'name': 'name', 'help': 'ENS name'},
        ]
    }


def hash_command(name):
    print(ens_utils.hash_name(name))

