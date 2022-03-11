from ctc import rpc


def get_command_spec():
    return {
        'f': async_call_command,
        'help': 'output result of a call',
        'args': [
            {'name': 'address', 'help': 'address to point call toward'},
            {'name': 'function-name', 'help': 'name of function to call'},
            {'name': 'args', 'nargs': '*', 'help': 'function arguments'},
            {
                'name': '--quiet',
                'action': 'store_true',
                'help': 'hide summary and only output function result',
            },
        ],
    }


async def async_call_command(address, function_name, args, quiet):

    if not quiet:
        print('performing eth_call')
        print('- to address:', address)
        print('- function:', function_name)
        print('- arguments:', args)
        print()
        print('result:')

    result = await rpc.async_eth_call(
        to_address=address,
        function_name=function_name,
        function_parameters=args,
    )
    print(result)

    await rpc.async_close_http_session()

