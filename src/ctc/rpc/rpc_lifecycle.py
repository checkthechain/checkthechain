from . import rpc_registry
from . import rpc_request


def construct(method, *, batch_parameter=None, batch_values=None, **parameters):
    """create an rpc request according to a specific method"""
    constructor = rpc_registry.get_constructors()[method]
    if batch_parameter is not None and batch_values is not None:
        return [
            constructor(**{batch_parameter: value}, **parameters)
            for value in batch_values
        ]
    else:
        return constructor(**parameters)


def digest(response, request, digest_kwargs=None):
    """process an rpc response"""
    if isinstance(request, dict):
        digestor = rpc_registry.get_digestors()[request['method']]
        return digestor(response=response, **digest_kwargs)
    elif isinstance(request, list):
        for subresponse, subrequest in zip(response, request):
            return [digest(subresponse, subrequest, digest_kwargs)]
    else:
        raise Exception()


def execute(request, provider=None, digest_kwargs=None):
    """send an rpc request and digest the corresponding response"""
    response = rpc_request.send(request=request, provider=provider)
    return digest(response, request=request, digest_kwargs=digest_kwargs)


async def async_execute(request, provider=None, **digest_kwargs):
    response = await rpc_request.async_send(request=request, provider=provider)
    return digest(response, **digest_kwargs)

