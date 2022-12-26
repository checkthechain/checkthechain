from __future__ import annotations

from ctc import spec
from .. import rpc_request


def construct_eth_gas_price() -> spec.RpcSingularRequest:
    return rpc_request.create('eth_gasPrice', [])


def construct_eth_accounts() -> spec.RpcSingularRequest:
    return rpc_request.create('eth_accounts', [])


def construct_eth_sign(
    address: spec.Address, message: str
) -> spec.RpcSingularRequest:
    return rpc_request.create('eth_sign', [address, message])


def construct_eth_sign_transaction(
    from_address: spec.Address,
    data: str,
    *,
    to_address: spec.Address | None = None,
    gas: int | None = None,
    gas_price: int | None = None,
    value: int | None = None,
    nonce: str | None = None,
) -> spec.RpcSingularRequest:

    parameters = {
        'from': from_address,
        'to': to_address,
        'gas': gas,
        'gasPrice': gas_price,
        'value': value,
        'data': data,
        'nonce': nonce,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    return rpc_request.create('eth_signTransaction', [parameters])


def construct_eth_send_transaction(
    from_address: spec.BinaryData,
    data: spec.BinaryData,
    *,
    to_address: spec.BinaryData | None = None,
    gas: int | None = None,
    gas_price: int | None = None,
    value: int | None = None,
    nonce: spec.BinaryData | None = None,
) -> spec.RpcSingularRequest:
    parameters = {
        'from': from_address,
        'to': to_address,
        'gas': gas,
        'gasPrice': gas_price,
        'value': value,
        'data': data,
        'nonce': nonce,
    }
    parameters = {k: v for k, v in parameters.items() if v is not None}

    return rpc_request.create('eth_sendTransaction', [parameters])


def construct_eth_send_raw_transaction(
    data: spec.BinaryData,
) -> spec.RpcSingularRequest:
    return rpc_request.create('eth_sendRawTransaction', [data])

