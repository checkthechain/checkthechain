from ctc import spec
from ctc.evm import binary_utils
from ctc.evm import contract_abi_utils


def digest_eth_call(
    response: spec.RpcSingularResponse,
    to_address: spec.BinaryData,
    function_abi_query: dict,
    decode_response: bool = True,
    delist_single_outputs: bool = True,
    package_named_outputs: bool = False,
) -> spec.RpcSingularResponse:

    if function_abi_query is None:
        raise NotImplementedError('parse function_abi from rpc_response')

    if decode_response:
        response = contract_abi_utils.decode_function_output(
            encoded_output=response,
            contract_address=to_address,
            delist_single_outputs=delist_single_outputs,
            package_named_outputs=package_named_outputs,
            **function_abi_query
        )

    return response


def digest_eth_estimate_gas(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_balance(
    response: spec.RpcSingularResponse, decode_response: bool = True
) -> spec.RpcSingularResponse:
    if decode_response:
        response = binary_utils.convert_binary_format(response, 'integer')
    return response


def digest_eth_get_storage_at(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response


def digest_eth_get_code(
    response: spec.RpcSingularResponse,
) -> spec.RpcSingularResponse:
    return response

