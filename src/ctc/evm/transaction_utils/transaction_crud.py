import toolparallel

from .. import rpc_utils


def get_transaction(transaction_hash, provider=None):
    return fetch_transaction(
        transaction_hash=transaction_hash, provider=provider
    )


def get_transactions(transaction_hashes, provider=None):
    return fetch_transaction(
        transaction_hashes=transaction_hashes, provider=provider
    )


@toolparallel.parallelize_input(
    singular_arg='transaction_hash',
    plural_arg='transaction_hashes',
)
def fetch_transaction(transaction_hash, provider=None):
    return rpc_utils.eth_get_transaction_by_hash(
        transaction_hash=transaction_hash,
        provider=provider,
    )

