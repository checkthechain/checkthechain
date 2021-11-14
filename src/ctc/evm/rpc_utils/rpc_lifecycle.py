import random

from ctc import config_utils
from . import rpc_backends
from . import rpc_digestors


def rpc_execute(
    *,
    rpc_data=None,
    method=None,
    parameters=None,
    batch_methods=None,
    batch_parameters=None,
    provider=None,
):
    if rpc_data is None:
        rpc_data = rpc_construct(
            method=method,
            parameters=parameters,
            batch_methods=batch_methods,
            batch_parameters=batch_parameters,
        )

    rpc_future = rpc_send(rpc_data=rpc_data, provider=provider)
    rpc_response = rpc_receive(rpc_future=rpc_future)
    return rpc_digest(rpc_response=rpc_response, rpc_future=rpc_future)


def rpc_construct(
    method=None, parameters=None, batch_methods=None, batch_parameters=None
):

    if method is not None and parameters is not None:
        return rpc_construct_call(method, parameters)
    elif batch_methods is not None and batch_parameters is not None:
        return rpc_construct_calls(batch_methods, batch_parameters)
    else:
        raise Exception('must specify more inputs')


def rpc_construct_call(method, parameters, id=None):
    if id is None:
        id = random.randint(1, 1e18)
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': id,
    }


def rpc_construct_calls(batch_methods, batch_parameters):

    # parse parameters
    n_calls = len(batch_parameters)
    ids = sorted(random.randint(1, 1e18) for c in range(len(n_calls)))

    # convert batch_methods to list if only one specified
    if isinstance(batch_methods, str):
        batch_methods = [batch_methods for c in range(n_calls)]

    # construct rpc calls
    rpc_calls = []
    for id, method, parameters in zip(ids, batch_methods, batch_parameters):
        rpc_calls.append(rpc_construct_call(method, parameters, id))

    return rpc_calls


def rpc_send(rpc_data, digest_kwargs=None, sync=True, provider=None):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if not isinstance(provider, str) and provider.startswith('http'):
        receipt = rpc_backends.rpc_call_http(rpc_data=rpc_data, provider=provider)
    else:
        raise Exception('unknown provider format: ' + str(provider))

    return {
        'batch': False,
        'pending': not sync,
        'provider': provider,
        'rpc_data': rpc_data,
        'digest_kwargs': digest_kwargs,
        'receipt': receipt,
    }


def rpc_receive(rpc_future, digest=True):
    if isinstance(rpc_future, list):
        return [rpc_receive(entry, digest=digest) for entry in rpc_future]

    if not rpc_future['pending']:
        response = rpc_future['receipt']
    else:
        raise NotImplementedError('async')

    if digest:
        response = rpc_digest(response, rpc_future)

    return response


def rpc_digest(rpc_response, rpc_future):
    has_digest_kwargs = rpc_future.get('digest_kwargs') is not None

    if rpc_future['batch']:

        digested_calls = []
        for r in range(len(rpc_response)):

            # get data specific to call
            response = rpc_response[r]
            method = rpc_future['rpc_data'][r]['method']
            if has_digest_kwargs:
                digest_kwargs = rpc_future['digest_kwargs'][r]
            else:
                digest_kwargs = {}

            # call digestor
            digestor = getattr(rpc_digestors, 'digest_' + method)
            digested_call = digestor(response=response, future=future, **digest_kwargs)
            digested_calls.append(digested_call)

        return digested_calls

    else:

        method = rpc_future['rpc_data']['method']
        digestor = getattr(rpc_digestors, 'digest_' + method)
        digest_kwargs = rpc_future['digest_kwargs']
        if digest_kwargs is None:
            digest_kwargs = {}
        digested_call = digestor(response=response, **digest_kwargs)

        return digested_call

