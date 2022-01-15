import asyncio

from ctc import rpc


def get_command_spec():
    return {
        'f': call_command,
        'args': [
            {'name': 'to_address'},
            {'name': 'function_name'},
            {'name': 'args', 'kwargs': {'nargs': '*'}},
        ],
    }


def call_command(to_address, function_name, args):

    asyncio.run(
        run(to_address=to_address, function_name=function_name, args=args)
    )


async def run(to_address, function_name, args):

    print('performing eth_call')
    print('to address:', to_address)
    print('function:', function_name)
    print('arguments:', args)
    print()
    result = rpc.async_eth_call(
        to_address=to_address,
        function_name=function_name,
        function_parameters=args,
    )
    print(result)

    from ctc.rpc.rpc_backends import rpc_http_async

    provider = rpc.get_provider()
    await rpc_http_async.async_close_session(provider=provider)

