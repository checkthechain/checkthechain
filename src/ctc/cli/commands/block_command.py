from ctc import evm


def get_command_spec():
    return {
        'f': block_command,
        'args': [
            {'name': 'block', 'kwargs': {'nargs': '?'}},
            {'name': '--timestamp', 'kwargs': {'type': int}},
            {'name': '--verbose', 'kwargs': {'action': 'store_true'}},
        ],
    }


def block_command(block, timestamp, verbose=False, **kwargs):
    if timestamp is not None and block is None:
        print('searching for block at timestamp:', timestamp)
        block = evm.get_block_of_timestamp(timestamp=timestamp, verbose=False)
        print('found block', block)
        print()

    evm.print_block_summary(block=block)

