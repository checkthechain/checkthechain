from ctc import rpc

from . import ens_directory
from . import resolver


async def async_get_owner(name, provider=None, block=None):
    node = resolver.hash_name(name)
    function_abi = {
        'name': 'owner',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'address'}],
    }
    return await rpc.async_eth_call(
        to_address=ens_directory.registry,
        function_abi=function_abi,
        function_parameters=[node],
        provider=provider,
        block_number=block,
    )


async def async_record_exists(name, provider=None, block=None):
    node = resolver.hash_name(name)
    function_abi = {
        'name': 'recordExists',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'bool'}],
    }
    return await rpc.async_eth_call(
        to_address=ens_directory.registry,
        function_abi=function_abi,
        function_parameters=[node],
        provider=provider,
        block_number=block,
    )


async def async_get_resolver(name, provider=None, block=None):
    node = resolver.hash_name(name)
    function_abi = {
        'name': 'resolver',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'address'}],
    }
    return await rpc.async_eth_call(
        to_address=ens_directory.registry,
        function_abi=function_abi,
        function_parameters=[node],
        provider=provider,
        block_number=block,
    )

