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

