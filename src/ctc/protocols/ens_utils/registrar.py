from __future__ import annotations

from ctc import evm
from ctc import rpc
from ctc import spec

from . import ens_directory
from . import resolver


async def async_get_owner(
    name: str,
    *,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> str:
    node = resolver.hash_name(name)
    function_abi: spec.FunctionABI = {
        'name': 'owner',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'address'}],
    }
    result = await rpc.async_eth_call(
        to_address=ens_directory.registry,
        function_abi=function_abi,
        function_parameters=[node],
        context=context,
        block_number=block,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_record_exists(
    name: str,
    *,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> bool:
    node = resolver.hash_name(name)
    function_abi: spec.FunctionABI = {
        'name': 'recordExists',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'bool'}],
    }
    result = await rpc.async_eth_call(
        to_address=ens_directory.registry,
        function_abi=function_abi,
        function_parameters=[node],
        context=context,
        block_number=block,
    )
    if not isinstance(result, bool):
        raise Exception('invalid rpc result')
    return result


async def async_get_resolver(
    name: str,
    *,
    block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> spec.Address:
    node = resolver.hash_name(name)
    function_abi: spec.FunctionABI = {
        'name': 'resolver',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'address'}],
    }
    result = await rpc.async_eth_call(
        to_address=ens_directory.registry,
        function_abi=function_abi,
        function_parameters=[node],
        context=context,
        block_number=block,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_registration_block(
    name: str, *, context: spec.Context = None
) -> int:

    if not name.endswith('.eth'):
        raise NotImplementedError()

    label, *parent = name.split('.')
    parent_node = resolver.hash_name('.'.join(parent))

    registrations: spec.DataFrame = await async_get_registrations(
        context=context
    )
    mask = (registrations['arg__label'] == evm.keccak_text(label)) & (
        registrations['arg__parent_node'] == parent_node
    )
    result = registrations[mask]

    if len(result) == 0:
        raise Exception('could not find registration')

    block = registrations['block_number'][0]

    if not isinstance(block, int):
        raise Exception('invalid rpc result')

    return block


async def async_get_registrations(
    *,
    context: spec.Context = None,
) -> spec.DataFrame:
    event_abi: spec.EventABI = {
        'name': 'NewOwner',
        'inputs': [
            {
                'indexed': True,
                'name': 'node',
                'type': 'bytes32',
            },
            {
                'indexed': True,
                'name': 'label',
                'type': 'bytes32',
            },
            {
                'indexed': False,
                'name': 'owner',
                'type': 'address',
            },
        ],
    }

    new_owners = await evm.async_get_events(
        contract_address='0x00000000000c2e074ec69a0dfb2997ba6c7d2e1e',
        event_abi=event_abi,
        start_block=9000000,
        verbose=False,
        context=context,
    )
    new_owners = new_owners.rename({'arg__node': 'arg__parent_node'})
    return new_owners

