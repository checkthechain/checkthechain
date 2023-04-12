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
    'cli_color_theme',
    'cli_chart_charset',
    'context_cache_rules',
)

config_int_subkeys = (
    'networks',
    'default_providers',
    'network_cache_configs',
)

context_keys = (
    'network',
    'provider',
    'cache',
)

schema_names = (
    #
    # admin schemas
    'schema_versions',
    #
    # generic schemas
    '4byte',
    'coingecko',
    #
    # network schemas
    'block_timestamps',
    'block_gas',
    'blocks',
    'contract_abis',
    'contract_creation_blocks',
    'dex_pools',
    'erc20_metadata',
    'events',
    'transactions',
    'chainlink',
)

network_schema_names = (
    'block_timestamps',
    'block_gas',
    'blocks',
    'contract_abis',
    'contract_creation_blocks',
    'dex_pools',
    'erc20_metadata',
    'events',
    'transactions',
    'chainlink',
)

# context_cache_keys: tuple[Literal['backend', 'read', 'write'], ...] = (
#     'backend',
#     'read',
#     'write',
# )

rpc_block_keys = (
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

db_block_keys = (
    'number',
    'hash',
    'timestamp',
    'miner',
    'extra_data',
    'base_fee_per_gas',
    'gas_limit',
    'gas_used',
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

transaction_keys_eip2930_camel = (
    'chainId',
    'nonce',
    'gasPrice',
    'gas',
    'to',
    'value',
    'input',
    'accessList',
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

transaction_keys_eip1559_camel = (
    'chainId',
    'nonce',
    'maxPriorityFeePerGas',
    'maxFeePerGas',
    'gas',
    'to',
    'value',
    'input',
    'accessList',
    'v',
    'r',
    's',
)

rpc_transaction_keys = {
    'access_list',
    'block_hash',
    'block_number',
    'chain_id',
    'from',
    'gas',
    'gas_price',
    'hash',
    'input',
    'max_fee_per_gas',
    'max_priority_fee_per_gas',
    'nonce',
    'r',
    's',
    'to',
    'transaction_index',
    'type',
    'v',
    'value',
}

db_transaction_keys = {
    'hash',
    'block_number',
    'transaction_index',
    'to_address',
    'from_address',
    'value',
    'input',
    'nonce',
    'transaction_type',
    'status',
    'gas_used',
    'gas_limit',
    'gas_priority',
    'gas_price',
    'gas_price_max',
    'access_list',
}

# removed_rpc_keys = {'v', 'r', 's', 'chain_id'}


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
    'disable_batch_requests',
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
    'disable_batch_requests': True,
}


#
# # events
#

event_index_fields = [
    'block_number',
    'transaction_index',
    'log_index',
]

decoded_event_fields = [
    'transaction_hash',
    'contract_address',
    'event_hash',
]

encoded_event_fields = [
    'transaction_hash',
    'contract_address',
    'event_hash',
    'topic1',
    'topic2',
    'topic3',
    'unindexed',
]

