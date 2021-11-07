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

