from ctc import evm


def get_command_spec():
    return {
        'f': transaction_command,
        'options': [
            {'name': 'transaction'},
            {'name': '--sort'},
        ],
    }


def transaction_command(transaction, sort, **kwargs):
    evm.print_transaction_summary(
        transaction_hash=transaction, sort_logs_by=sort
    )

