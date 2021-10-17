import toolparallel

from ctc.toolbox import web3_utils


def get_transactions(transaction_hashes):
    return fetch_transaction(transaction_hashes=transaction_hashes)


@toolparallel.parallelize_input(
    singular_arg='transaction_hash',
    plural_arg='transaction_hashes',
)
def fetch_transaction(transaction_hash):
    web3_instance = web3_utils.create_web3_instance()
    transaction = web3_instance.eth.getTransaction(transaction_hash=transaction_hash)
    return transaction

