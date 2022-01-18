
from .. import rpc_request


def construct_trace_transaction(transaction_hash):
    return rpc_request.create('trace_transaction', [transaction_hash])


def digest_trace_transaction(response):
    return response


async def async_trace_transaction(transaction_hash, provider=None):
    request = construct_trace_transaction(transaction_hash=transaction_hash)
    response = await rpc_request.async_send(request, provider=provider)
    return digest_trace_transaction(response=response)

