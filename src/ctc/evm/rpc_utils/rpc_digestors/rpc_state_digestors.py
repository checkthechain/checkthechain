from ... import binary_utils
from ... import contract_abi_utils


def digest_eth_call(
    response,
    future,
    to_address,
    function_abi_query,
    decode_response=True,
    delist_single_outputs=True,
    package_named_results=False,
):

    if function_abi_query is None:
        raise NotImplementedError('parse function_abi from rpc_response')

    if decode_response:
        response = contract_abi_utils.decode_function_output(
            encoded_output=response,
            contract_address=to_address,
            delist_single_outputs=delist_single_outputs,
            package_named_results=package_named_results,
            **function_abi_query
        )

    return response


def digest_eth_estimate_gas(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_balance(response, decode_response=True):
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_storage_at(response):
    return response


def digest_eth_get_code(response):
    return response

