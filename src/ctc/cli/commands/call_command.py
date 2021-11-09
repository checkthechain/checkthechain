from ctc.evm import rpc_utils


def get_command_spec():
    return {
        'f': call_command,
        'options': [
            {'name': 'to_address'},
            {'name': 'function_name'},
            {'name': 'args', 'kwargs': {'nargs': '*'}},
        ],
    }


def call_command(to_address, function_name, args, **kwargs):
    print('performing eth_call')
    print('to address:', to_address)
    print('function:', function_name)
    print('arguments:', args)
    print()
    result = rpc_utils.eth_call(
        to_address=to_address,
        function_name=function_name,
        function_parameters=args,
    )
    print(result)

