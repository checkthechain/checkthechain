from ctc import rpc


async def async_get_underlying_asset(pool_token, provider=None):
    function_abi = {
        'name': 'UNDERLYING_ASSET_ADDRESS',
        'inputs': [],
        'outputs': [{'type': 'address'}],
    }
    return await rpc.async_eth_call(
        to_address=pool_token,
        function_abi=function_abi,
        provider=provider,
    )

