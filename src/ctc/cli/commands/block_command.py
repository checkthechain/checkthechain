from ctc import evm


def get_command_spec():
    return {
        'f': block_command,
        'args': [
            {'name': 'block'},
            {'name': '--verbose', 'kwargs': {'action': 'store_true'}},
        ],
    }


def block_command(block, verbose=False, **kwargs):
    evm.print_block_summary(block=block)

