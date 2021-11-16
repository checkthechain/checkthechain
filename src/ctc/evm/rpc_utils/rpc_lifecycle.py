import random

from ctc import config_utils
from . import rpc_backends
from . import rpc_crud
from . import rpc_digestors


def rpc_execute(
    *,
    rpc_request=None,
    method=None,
    parameters=None,
    batch_methods=None,
    batch_parameters=None,
    provider=None,
    digest_kwargs=None,
):
    if rpc_request is None:
        rpc_request = rpc_construct(
            method=method,
            parameters=parameters,
            batch_methods=batch_methods,
            batch_parameters=batch_parameters,
        )

    rpc_future = rpc_send(
        rpc_request=rpc_request,
        provider=provider,
        digest_kwargs=digest_kwargs,
    )
    rpc_response = rpc_receive(rpc_future=rpc_future)
    return rpc_digest(rpc_response=rpc_response, rpc_future=rpc_future)


def rpc_construct(
    method=None, parameters=None, batch_methods=None, batch_parameters=None
):

    if method is not None and parameters is not None:
        return {
            'jsonrpc': '2.0',
            'method': method,
            'params': parameters,
            'id': random.randint(1, 1e18),
        }

    elif batch_methods is not None and batch_parameters is not None:

        # parse parameters
        n_calls = len(batch_parameters)
        ids = sorted(random.randint(1, 1e18) for c in range(len(n_calls)))

        # convert batch_methods to list if only one specified
        if isinstance(batch_methods, str):
            batch_methods = [batch_methods for c in range(n_calls)]

        # construct rpc calls
        rpc_calls = []
        for id, method, parameters in zip(ids, batch_methods, batch_parameters):
            rpc_call = {
                'jsonrpc': '2.0',
                'method': method,
                'params': parameters,
                'id': id,
            }
            rpc_calls.append(rpc_call)

        return rpc_calls

    else:
        raise Exception('must specify more inputs')


def rpc_send(rpc_request, digest_kwargs=None, sync=True, provider=None):

    if provider is None:
        config = config_utils.get_config()
        provider = config['export_provider']

    if isinstance(provider, str) and provider.startswith('http'):
        receipt = rpc_backends.rpc_call_http(
            rpc_request=rpc_request, provider=provider
        )
    else:
        raise Exception('unknown provider format: ' + str(provider))

    return {
        'batch': not isinstance(rpc_request, dict),
        'pending': not sync,
        'provider': provider,
        'rpc_request': rpc_request,
        'digest_kwargs': digest_kwargs,
        'receipt': receipt,
    }


def rpc_receive(rpc_future):
    if isinstance(rpc_future, list):
        return [rpc_receive(entry) for entry in rpc_future]

    if not rpc_future['pending']:
        response = rpc_future['receipt']
    else:
        raise NotImplementedError('async')

    return response


def rpc_digest(rpc_response, rpc_future):
    all_digest_kwargs = rpc_future.get('digest_kwargs')

    if rpc_future['batch']:

        digested_calls = []
        for r in range(len(rpc_response)):

            # get data specific to call
            response = rpc_response[r]
            if all_digest_kwargs is not None:
                if isinstance(all_digest_kwargs, dict):
                    digest_kwargs = all_digest_kwargs
                else:
                    digest_kwargs = rpc_future['digest_kwargs'][r]
            else:
                digest_kwargs = {}

            # call digestor
            method = rpc_future['rpc_request'][r]['method']
            method = rpc_crud.camel_case_to_snake_case(method)
            digestor = getattr(rpc_digestors, 'digest_' + method)
            digested_call = digestor(
                response=response, future=rpc_future, **digest_kwargs
            )
            digested_calls.append(digested_call)

        return digested_calls

    else:

        method = rpc_future['rpc_request']['method']
        method = rpc_crud.camel_case_to_snake_case(method)
        digestor = getattr(rpc_digestors, 'digest_' + method)
        if all_digest_kwargs is None:
            digest_kwargs = {}
        else:
            digest_kwargs = all_digest_kwargs
        digested_call = digestor(response=rpc_response, future=rpc_future, **digest_kwargs)

        return digested_call

