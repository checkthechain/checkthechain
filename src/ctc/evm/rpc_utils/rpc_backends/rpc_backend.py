from ctc import config_utils
from . import rpc_http


def rpc_call(method, parameters, provider=None):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if isinstance(provider, str) and provider.startswith('http'):
        return rpc_http.rpc_call_http(
            method=method, parameters=parameters, provider=provider,
        )
    else:
        raise Exception('unknown provider format: ' + str(provider))



def rpc_send(rpc_call, sync=True, provider=None):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if not isinstance(provider, str) and provider.startswith('http'):
        result = rpc_http.rpc_call_http(rpc_call=rpc_call, provider=provider)
    else:
        raise Exception('unknown provider format: ' + str(provider))

    return {
        'batch': False,
        'pending': not sync,
        'provider': provider,
        'id': rpc_call['id'],
        'result': result,
    }


def rpc_batch_send(rpc_calls, provider=None):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if isinstance(provider, str) and provider.startswith('http'):
        return rpc_http.rpc_call_http(rpc_calls=rpc_calls, provider=provider)
    else:
        raise Exception('unknown provider format: ' + str(provider))

    return {
        'batch': True,
        'provider': provider,
        'id': rpc_call['id'],
    }


