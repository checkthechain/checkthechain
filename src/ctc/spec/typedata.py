"""type information that should be available to other modules

(type definitions are only loaded while type checking via typing.TYPE_CHECKING)
"""

from __future__ import annotations


config_keys = (
    'config_spec_version',
    'data_dir',
    'providers',
    'networks',
    'default_network',
    'default_providers',
    'db_configs',
    'log_rpc_calls',
    'log_sql_queries',
)

block_keys = (
    'base_fee_per_gas',
    'difficulty',
    'extra_data',
    'gas_limit',
    'gas_used',
    'hash',
    'logs_bloom',
    'miner',
    'mix_hash',
    'nonce',
    'number',
    'parent_hash',
    'receipts_root',
    'sha3_uncles',
    'size',
    'state_root',
    'timestamp',
    'total_difficulty',
    'transactions',
    'transactions_root',
    'uncles',
)

block_number_names = ['latest', 'earliest', 'pending']

block_keys_standardized = {
    'uncle_hashes': 'sha3_uncles',
    'coinbase': 'miner',
    'author': 'miner',
    'beneficiary': 'miner',
    'transaction_root': 'transactions_root',
    'bloom': 'logs_bloom',
    'block_number': 'number',
    'proof_of_work': 'mix_hash',
}


#
# # transactions
#

transaction_keys_legacy = (
    'nonce',
    'gas_price',
    'gas',
    'to',
    'value',
    'input',
    'v',
    'r',
    's',
)

transaction_keys_eip2930 = (
    'chain_id',
    'nonce',
    'gas_price',
    'gas',
    'to',
    'value',
    'input',
    'access_list',
    'v',
    'r',
    's',
)

transaction_keys_eip1559 = (
    'chain_id',
    'nonce',
    'max_priority_fee_per_gas',
    'max_fee_per_gas',
    'gas',
    'to',
    'value',
    'input',
    'access_list',
    'v',
    'r',
    's',
)

transaction_keys_standardized = {
    'chainId': 'chain_id',
    'start_gas': 'gas',
    'maxPriorityFeePerGas': 'max_priority_fee_per_gas',
    'maxFeePerGas': 'max_fee_per_gas',
    'gas_limit': 'gas',
    'destination': 'to',
    'amount': 'value',
    'data': 'input',
    'accessList': 'access_list',
    'signature_y_parity': 'v',
    'signature_r': 'r',
    'signature_s': 's',
}


#
# # providers
#

provider_keys = [
    'url',
    'name',
    'network',
    'protocol',
    'session_kwargs',
    'chunk_size',
    'convert_reverts_to_none',
]

default_provider_settings = {
    # these must be particularly specified
    # 'url',
    # 'network',
    # 'protocol',
    #
    'name': '',
    'session_kwargs': {},
    'chunk_size': None,
    'convert_reverts_to_none': False,
}
