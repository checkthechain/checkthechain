from ctc import binary
from ctc import evm
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


async def async_get_registration_block(name):

    if not name.endswith('.eth'):
        raise NotImplementedError()

    label, *parent = name.split('.')
    parent_node = resolver.hash_name('.'.join(parent))

    registrations = await async_get_registrations()
    mask = (registrations['arg__label'] == binary.keccak_text(label)) * (
        registrations['arg__parent_node'] == parent_node
    )
    result = registrations[mask]

    if len(result) == 0:
        raise Exception('could not find registration')

    block = result.iloc[0].name[0]

    return block


async def async_get_registrations():
    new_owners = await evm.async_get_events(
        contract_address='0x00000000000c2e074ec69a0dfb2997ba6c7d2e1e',
        event_name='NewOwner',
        start_block=9000000,
    )
    new_owners['arg__parent_node'] = new_owners.pop('arg__node')
    return new_owners

