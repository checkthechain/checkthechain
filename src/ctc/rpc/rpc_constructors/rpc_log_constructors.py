from ctc import spec
from .. import rpc_format
from .. import rpc_request


def construct_eth_new_filter(
    contract_address: spec.BinaryData = None,
    topics: list[spec.BinaryData] = None,
    start_block: spec.BlockSpec = None,
    end_block: spec.BlockSpec = None,
) -> spec.RpcRequest:
    if start_block is not None:
        start_block = rpc_format.encode_block_number(start_block)
    if end_block is not None:
        end_block = rpc_format.encode_block_number(end_block)

    parameters = {
        'address': contract_address,
        'topics': topics,
        'fromBlock': start_block,
        'toBlock': end_block,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    return rpc_request.create('eth_newFilter', [parameters])


def construct_eth_new_block_filter() -> spec.RpcRequest:
    return rpc_request.create('eth_newBlockFilter', [])


def construct_eth_new_pending_transaction_filter() -> spec.RpcRequest:
    return rpc_request.create('eth_newPendingTransactionFilter', [])


def construct_eth_uninstall_filter(filter_id) -> spec.RpcRequest:
    return rpc_request.create('eth_uninstallFilter', [filter_id])


def construct_eth_get_filter_changes(filter_id) -> spec.RpcRequest:
    return rpc_request.create('eth_getFilterChanges', [filter_id])


def construct_eth_get_filter_logs(filter_id) -> spec.RpcRequest:
    return rpc_request.create('eth_getFilterLogs', [filter_id])


def construct_eth_get_logs(
    contract_address=None,
    topics=None,
    start_block=None,
    end_block=None,
) -> spec.RpcRequest:
    if start_block is not None:
        start_block = rpc_format.encode_block_number(start_block)
    if end_block is not None:
        end_block = rpc_format.encode_block_number(end_block)

    parameters = {
        'address': contract_address,
        'topics': topics,
        'fromBlock': start_block,
        'toBlock': end_block,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    return rpc_request.create('eth_getLogs', [parameters])

