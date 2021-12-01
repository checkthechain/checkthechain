contenttypes = {
    'Call': {
        'jsonrpc': 'Text',
        'method': 'Text',
        'params': 'Map',
        'id': 'Integer',
    },
    'Request': ['Call', ['Call']],
    'Response': {},
    'Provider': {
        'type': ['http', 'websocket'],
        'url': 'Text',
        'session_kwargs': 'Map',
    },
}

#
# # rpc call schema
#

rpc_block_quantities = [
    'baseFeePerGas',
    'number',
    'difficulty',
    'totalDifficulty',
    'size',
    'gasLimit',
    'gasUsed',
    'timestamp',
]
rpc_log_quantities = [
    'logIndex',
    'transactionIndex',
    'blockNumber',
]
rpc_transaction_quantities = [
    'blockNumber',
    'gas',
    'gasPrice',
    'maxFeePerGas',
    'maxPriorityFeePerGas',
    'nonce',
    'transactionIndex',
    'value',
    'v',
]
rpc_transaction_receipt_quantities = [
    'transactionIndex',
    'blockNumber',
    'cumulativeGasUsed',
    'effectiveGasPrice',
    'gasUsed',
    'quantity',
    'status',
]

rpc_result_scalar_quantities = [
    'eth_blockNumber',
    'eth_getUncleCountByBlockHash',
    'eth_getUncleCountByBlockNumber',
    'eth_newFilter',
    'eth_newBlockFilter',
    'eth_newPendingTransactionFilter',
]
rpc_result_map_quantities = {
    'eth_getBlockByHash': rpc_block_quantities,
    'eth_getBlockByNumber': rpc_block_quantities,
    'eth_getUncleByBlockHashAndIndex': rpc_block_quantities,
    'eth_getUncleByBlockNumberAndIndex': rpc_block_quantities,
}
rpc_result_list_map_quantities = {
    'eth_getLogs': rpc_log_quantities,
}


rpc_constructor_batch_inputs = {
    'eth_get_block_by_hash': {'block_hashes': 'block_hash'},
    'eth_get_block_by_number': {'block_numbers': 'block_number'},
    'eth_get_uncle_count_by_block_hash': {'block_hashes': 'block_hash'},
    'eth_get_uncle_count_by_block_number': {'block_numbers': 'block_number'},
    'eth_compile_lll': {'codes': 'code'},
    'eth_compile_solidity': {'codes': 'code'},
    'eth_compile_serpent': {'codes': 'code'},
    'eth_get_logs': {
        'topic_lists': 'topic',
        'addresses': 'addresses',
        'block_hashes': 'block_hash',
    },
    'web3_sha3': {'datas': 'data'},
    'eth_call': {
        'to_addresses': 'to_address',
        'block_numbers': 'block_number',
        'function_parameter_list': 'function_parameters',
    },
    'eth_estimate_gas': {
        'to_addresses': 'to_address',
        'block_numbers': 'block_number',
        'function_parameter_list': 'function_parameters',
    },
    'eth_get_balance': {
        'addresses': 'address',
        'block_numbers': 'block_number',
    },
    'eth_get_storage_at': {
        'addresses': 'address',
        'positions': 'position',
        'block_numbers': 'block_number',
    },
    'eth_get_code': {'addresses': 'address', 'block_numbers': 'block_number'},
    'eth_send_raw_transaction': {'datas': 'data'},
    'eth_get_transaction_count': {
        'addresses': 'address',
        'block_numbers': 'block_number',
    },
    'eth_get_transaction_by_hash': {'transaction_hashes': 'transaction_hash'},
    'eth_get_transaction_by_block_hash_and_index': {
        'block_hashes': 'block_hash',
        'indices': 'index',
    },
    'eth_get_transaction_by_block_number_and_index': {
        'block_numbers': 'block_number',
        'indices': 'index',
    },
    'eth_get_transaction_receipt': {'transaction_hashes': 'transaction_hash'},
    'eth_get_block_transaction_count_by_hash': {'block_hashes': 'block_hash'},
    'eth_get_block_transaction_count_by_number': {
        'block_numbers': 'block_number'
    },
}

