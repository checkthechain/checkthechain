import asyncio

from ctc import binary
from ctc import evm
from ctc import rpc

from . import ens_directory
from . import registrar


def hash_name(name):
    import idna  # type: ignore

    labels = name.split('.')
    output = '00' * 32
    for label in labels[::-1]:
        label = idna.encode(label, uts46=True)
        label_hash = binary.keccak_text(label, output_format='raw_hex')
        output = binary.keccak(output + label_hash, output_format='raw_hex')
    return '0x' + output


async def async_resolve_name(name, provider=None, block=None):
    name_hash = hash_name(name)

    result = await rpc.async_eth_call(
        to_address=ens_directory.resolver,
        block_number=block,
        function_name='addr',
        function_abi={
            'name': 'addr',
            'inputs': [{'type': 'bytes32'}],
            'outputs': [{'type': 'address'}],
        },
        function_parameters=[name_hash],
        provider=provider,
    )

    if result == '0x0000000000000000000000000000000000000000':
        resolver = await registrar.async_get_resolver(
            name=name, provider=provider, block=block
        )
        result = await rpc.async_eth_call(
            to_address=resolver,
            block_number=block,
            function_name='addr',
            function_abi={
                'name': 'addr',
                'inputs': [{'type': 'bytes32'}],
                'outputs': [{'type': 'address'}],
            },
            function_parameters=[name_hash],
            provider=provider,
        )

    return result


async def async_reverse_lookup(address, provider=None, block=None):
    names = await rpc.async_eth_call(
        to_address=ens_directory.reverse_records,
        block_number=block,
        function_abi={
            'name': 'getNames',
            'inputs': [{'type': 'address[]'}],
            'outputs': [{'type': 'string[]'}],
        },
        function_parameters=[[address]],
        provider=provider,
    )
    return names[0]


def name_history():
    pass


async def async_get_text_record(key, name=None, node=None):

    if node is None:
        node = hash_name(name)

    return await rpc.async_eth_call(
        to_address=ens_directory.resolver,
        function_name='text',
        function_parameters=[node, key],
    )


async def async_get_text_records(name=None, node=None, keys=None):
    """
    https://docs.ens.domains/ens-improvement-proposals/ensip-5-text-records
    """

    if node is None:
        node = hash_name(name)

    if keys is None:
        text_changes = await async_get_text_changes(name=name, node=node)
        keys = list(text_changes['arg__key'].values)

    coroutines = [async_get_text_record(key=key, node=node) for key in keys]
    values = await asyncio.gather(*coroutines)
    return dict(zip(keys, values))


async def async_get_text_changes(name=None, node=None):

    events = await evm.async_get_events(
        contract_address=ens_directory.resolver,
        event_name='TextChanged',
        start_block=9000000,
        verbose=False,
    )

    if node is None:
        node = hash_name(name)

    mask = events['arg__node'] == node
    return events[mask]


async def async_get_content_hash(name=None, node=None):

    if node is None:
        node = hash_name(name)

    return rpc.async_eth_call(
        to_address=ens_directory.resolver,
        function_name='contentHash',
        function_parameters=[node],
    )


async def async_get_expiration(name):

    if not name.endswith('.eth'):
        raise NotImplementedError('only implemented for .eth domains')

    label = name.split('.')[-2]
    label_id = binary.keccak_text(label, output_format='integer')

    return await rpc.async_eth_call(
        to_address=ens_directory.base_registrar,
        function_name='nameExpires',
        function_parameters=[label_id],
    )

