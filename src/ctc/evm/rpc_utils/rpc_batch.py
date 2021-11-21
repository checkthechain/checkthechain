from . import rpc_constructors
from . import rpc_lifecycle


def batch_eth_call(
    to_address,
    from_address=None,
    gas=None,
    gas_price=None,
    value_sent=None,
    block_numbers=None,
    call_data=None,
    function_parameters=None,
    provider=None,
    decode_response=True,
    delist_single_outputs=True,
    package_named_results=False,
    **function_abi_query
):
    rpc_request = rpc_constructors.construct_rpc_eth_call(
        to_address,
        from_address=from_address,
        gas=gas,
        gas_price=gas_price,
        value_sent=value_sent,
        block_numbers=block_numbers,
        call_data=call_data,
        function_parameters=function_parameters,
        **function_abi_query
    )

    digest_kwargs = dict(
        to_address=to_address,
        decode_response=decode_response,
        delist_single_outputs=delist_single_outputs,
        package_named_results=package_named_results,
        function_abi_query=function_abi_query,
    )

    return rpc_lifecycle.rpc_execute(
        rpc_request=rpc_request,
        provider=provider,
        digest_kwargs=digest_kwargs,
    )


def batch_eth_get_code(
    address=None, block_number=None, addresses=None, block_numbers=None, provider=None,
):
    if addresses is None and address is None:
        raise Exception('must specify address or addresses')
    if block_number is None and block_numbers is None:
        raise Exception('must specify block_number or block_numbers')

    if addresses is None:
        addresses = [address]
    if block_numbers is None:
        block_numbers = [block_number]

    rpc_request = []
    for block_number in block_numbers:
        for address in addresses:
            call = rpc_constructors.construct_eth_get_code(
                address=address, block_number=block_number
            )
            rpc_request.append(call)

    result = rpc_lifecycle.rpc_execute(
        rpc_request=rpc_request,
        provider=provider,
        digest_kwargs={},
    )

    packaged = {}
    result_iter = iter(result)
    for block_number in block_numbers:
        packaged.setdefault(block_number, {})
        for address in addresses:
            packaged[block_number][address] = next(result_iter)

    return packaged

