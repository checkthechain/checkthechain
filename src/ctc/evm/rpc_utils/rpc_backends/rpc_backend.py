from ctc import config_utils
from .. import rpc_lifecycle
from . import rpc_http


def rpc_call(method, parameters, provider=None):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    rpc_data = rpc_lifecycle.rpc_construct(method=method, parameters=parameters)
    if isinstance(provider, str) and provider.startswith('http'):
        return rpc_http.rpc_call_http(rpc_data=rpc_data, provider=provider)
    else:
        raise Exception('unknown provider format: ' + str(provider))

