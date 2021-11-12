from ... import binary_utils
from .. import rpc_backends
from .. import rpc_crud
from .. import rpc_spec


def eth_new_filter(
    contract_address=None,
    topics=None,
    start_block=None,
    end_block=None,
    provider=None,
    decode_result=False,
):
    if start_block is not None:
        start_block = rpc_crud.encode_rpc_block(start_block)
    if end_block is not None:
        end_block = rpc_crud.encode_rpc_block(end_block)

    parameters = {
        'address': contract_address,
        'topics': topics,
        'fromBlock': start_block,
        'toBlock': end_block,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    result = rpc_backends.rpc_call(
        method='eth_newFilter',
        parameters=[parameters],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_new_block_filter(provider=None, decode_result=False):

    result = rpc_backends.rpc_call(
        method='eth_newBlockFilter',
        parameters=[],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_new_pending_transaction_filter(provider=None, decode_result=False):
    result = rpc_backends.rpc_call(
        method='eth_newPendingTransactionFilter',
        parameters=[],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_uninstall_filter(filter_id, provider=None, decode_result=False):
    result = rpc_backends.rpc_call(
        method='eth_uninstallFilter',
        parameters=[filter_id],
        provider=provider,
    )

    if decode_result:
        result = binary_utils.convert_binary_format(result, 'integer')

    return result


def eth_get_filter_changes(
    filter_id, provider=None, decode_result=True, snake_case_result=True, include_removed=False,
):

    result = rpc_backends.rpc_call(
        method='eth_getFilterChanges',
        parameters=[filter_id],
        provider=provider,
    )

    if not include_removed and len(result) > 0 and isinstance(result[0], dict):
        result = [subresult for subresult in result if not subresult['removed']]

    if decode_result and len(result) > 0 and isinstance(result[0], dict):
        result = [
            rpc_crud.decode_rpc_map(subresult, rpc_spec.rpc_log_quantities)
            for subresult in result
        ]

    if snake_case_result and len(result) > 0 and isinstance(result[0], dict):
        result = [
            rpc_crud.rpc_keys_to_snake_case(subresult) for subresult in result
        ]

    return result


def eth_get_filter_logs(
    filter_id, provider=None, decode_result=True, snake_case_result=True, include_removed=False,
):

    result = rpc_backends.rpc_call(
        method='eth_getFilterLogs',
        parameters=[filter_id],
        provider=provider,
    )

    if not include_removed:
        result = [subresult for subresult in result if not subresult['removed']]

    if decode_result and len(result) > 0 and isinstance(result[0], dict):
        result = [
            rpc_crud.decode_rpc_map(subresult, rpc_spec.rpc_log_quantities)
            for subresult in result
        ]

    if snake_case_result and len(result) > 0 and isinstance(result[0], dict):
        result = [
            rpc_crud.rpc_keys_to_snake_case(subresult) for subresult in result
        ]

    return result


def eth_get_logs(
    contract_address=None,
    topics=None,
    start_block=None,
    end_block=None,
    provider=None,
    decode_result=True,
    snake_case_result=True,
    include_removed=False,
):
    if start_block is not None:
        start_block = rpc_crud.encode_rpc_block(start_block)
    if end_block is not None:
        end_block = rpc_crud.encode_rpc_block(end_block)

    parameters = {
        'address': contract_address,
        'topics': topics,
        'fromBlock': start_block,
        'toBlock': end_block,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    result = rpc_backends.rpc_call(
        method='eth_getLogs',
        parameters=[parameters],
        provider=provider,
    )

    if not include_removed:
        result = [subresult for subresult in result if not subresult['removed']]

    if decode_result and len(result) > 0 and isinstance(result[0], dict):
        result = [
            rpc_crud.decode_rpc_map(subresult, rpc_spec.rpc_log_quantities)
            for subresult in result
        ]

    if snake_case_result and len(result) > 0 and isinstance(result[0], dict):
        result = [
            rpc_crud.rpc_keys_to_snake_case(subresult) for subresult in result
        ]

    return result

