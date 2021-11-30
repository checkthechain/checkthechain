"""
digestors are simpler than constructors and so they do not have batch versions
"""

import inspect
import typing

from ctc import spec
from .. import rpc_registry
from .. import rpc_request
from .. import rpc_spec


#
# # batch construction
#


def batch_construct(method: str, **constructor_kwargs) -> spec.RpcPluralRequest:
    batch_inputs = _get_batch_constructor_inputs(method=method)
    if len(batch_inputs) == 0:
        raise Exception('no batch inputs available for method: ' + str(method))
    singular_constructor = rpc_registry.get_constructor(method=method)
    parameter, values, constructor_kwargs = _get_batch_parameter(
        constructor_kwargs,
        batch_inputs,
    )
    return [
        singular_constructor(**{parameter: value}, **constructor_kwargs)
        for value in values
    ]


def _get_batch_parameter(kwargs, batch_inputs):

    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    # find suitable candidates
    candidates = []
    for plural_name, singular_name in batch_inputs.items():
        if plural_name in kwargs:
            candidates.append(plural_name)

    # select candidate
    if len(candidates) == 0:
        raise Exception('no batch parameter specified')
    elif len(candidates) > 1:
        raise Exception('too many batch parameters specified')
    else:
        parameter = candidates[0]
        return (
            batch_inputs[parameter],
            kwargs[parameter],
            {k: v for k, v in kwargs.items() if k not in batch_inputs},
        )


def _get_batch_constructor_inputs(method: str) -> dict[str, str]:
    return rpc_spec.rpc_constructor_batch_inputs.get(method, {})


#
# # batch execution
#


def batch_execute(
    method: str, *, provider: spec.ProviderSpec = None, **kwargs
) -> spec.RpcPluralResponse:

    constructor_kwargs, digestor_kwargs = _separate_execution_kwargs(
        method=method,
        kwargs=kwargs,
    )
    request = batch_construct(method=method, **constructor_kwargs)
    response = rpc_request.send(request=request, provider=provider)
    digestor = rpc_registry.get_digestor(method)
    return [
        digestor(subresponse, **digestor_kwargs) for subresponse in response
    ]


async def async_batch_execute(
    method: str, *, provider: spec.ProviderSpec = None, **kwargs
) -> spec.RpcPluralResponse:

    constructor_kwargs, digestor_kwargs = _separate_execution_kwargs(
        method=method,
        kwargs=kwargs,
    )
    request = batch_construct(method=method, **constructor_kwargs)
    response = await rpc_request.async_send(request=request, provider=provider)
    digestor = rpc_registry.get_digestor(method)
    return [
        digestor(subresponse, **digestor_kwargs) for subresponse in response
    ]


def _separate_execution_kwargs(
    method: str,
    kwargs: dict[str, typing.Any],
) -> tuple[dict[str, typing.Any], dict[str, typing.Any]]:

    # compile digestor kwargs
    digestor = rpc_registry.get_digestor(method)
    signature = inspect.getfullargspec(digestor)
    digestor_args = signature.args + signature.kwonlyargs

    # separate kwargs into constructor and digestor kwargs
    constructor_kwargs = {}
    digestor_kwargs = {}
    for key, value in kwargs.items():
        if key in digestor_args:
            digestor_kwargs[key] = value
        else:
            constructor_kwargs[key] = value

    # add args that are passed to both constructors and digestors
    if method == 'eth_call':
        function_abi_query = [
            'function_name',
            'contract_abi',
            'contract_address',
            'n_parameters',
            'parameter_types',
            'function_selector',
        ]
        constructor_kwargs['to_address'] = kwargs['to_address']
        digestor_kwargs['function_abi_query'] = {
            arg: kwargs[arg]
            for arg in function_abi_query
            if arg in kwargs
        }

    return constructor_kwargs, digestor_kwargs

