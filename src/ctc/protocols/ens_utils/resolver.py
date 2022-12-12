from __future__ import annotations

import typing

from ctc import evm
from ctc import rpc
from ctc import spec

from . import ens_directory
from . import registrar


def hash_name(name: str) -> spec.PrefixHexData:
    import idna

    labels = name.split('.')
    output = '00' * 32
    for label in labels[::-1]:
        label_bytes = idna.encode(label, uts46=True)
        label_hash = evm.keccak_text(label_bytes, output_format='raw_hex')
        output = evm.keccak(output + label_hash, output_format='raw_hex')
    return '0x' + output


async def async_resolve_name(
    name: str,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address | None:
    name_hash = hash_name(name)

    function_abi: spec.FunctionABI = {
        'name': 'addr',
        'inputs': [{'type': 'bytes32'}],
        'outputs': [{'type': 'address'}],
    }

    result = await rpc.async_eth_call(
        to_address=ens_directory.resolver,
        block_number=block,
        function_abi=function_abi,
        function_parameters=[name_hash],
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')

    if result == '0x0000000000000000000000000000000000000000':
        resolver = await registrar.async_get_resolver(
            name=name, provider=provider, block=block
        )
        if resolver == '0x0000000000000000000000000000000000000000':
            return None
        result = await rpc.async_eth_call(
            to_address=resolver,
            block_number=block,
            function_abi={
                'name': 'addr',
                'inputs': [{'type': 'bytes32'}],
                'outputs': [{'type': 'address'}],
            },
            function_parameters=[name_hash],
            provider=provider,
        )
        if not isinstance(result, str):
            raise Exception('invalid rpc result')

    return result


async def async_resolve_names(
    names: typing.Sequence[str],
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> typing.Sequence[spec.Address | None]:

    import asyncio

    coroutines = [
        async_resolve_name(name=name, provider=provider, block=block)
        for name in names
    ]

    return await asyncio.gather(*coroutines)


async def async_reverse_lookup(
    address: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> str:
    function_abi: spec.FunctionABI = {
        'name': 'getNames',
        'inputs': [{'type': 'address[]'}],
        'outputs': [{'type': 'string[]'}],
    }
    names = await rpc.async_eth_call(
        to_address=ens_directory.reverse_records,
        block_number=block,
        function_abi=function_abi,
        function_parameters=[[address]],
        provider=provider,
    )
    output = names[0]
    if not isinstance(output, str):
        raise Exception('invalid rpc result')
    return output


async def async_name_history() -> None:
    raise NotImplementedError()


async def async_get_text_record(
    key: str,
    *,
    name: str | None = None,
    node: str | None = None,
) -> str:

    if node is None:
        if name is None:
            raise Exception('must specify name or node')
        node = hash_name(name)

    function_abi: spec.FunctionABI = {
        'name': 'text',
        'inputs': [
            {'name': 'node', 'type': 'bytes32'},
            {'name': 'key', 'type': 'string'},
        ],
        'outputs': [{'name': '', 'type': 'string'}],
    }

    result = await rpc.async_eth_call(
        to_address=ens_directory.resolver,
        function_abi=function_abi,
        function_parameters=[node, key],
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_text_records(
    *,
    name: str | None = None,
    node: str | None = None,
    keys: typing.Sequence[str] | None = None,
) -> dict[str, str]:
    """
    https://docs.ens.domains/ens-improvement-proposals/ensip-5-text-records
    """
    import asyncio

    if node is None:
        if name is None:
            raise Exception('must specify name or node')
        node = hash_name(name)

    if keys is None:
        text_changes = await async_get_text_changes(name=name, node=node)
        keys = list(text_changes['arg__key'].values)

    coroutines = [async_get_text_record(key=key, node=node) for key in keys]
    values = await asyncio.gather(*coroutines)
    return dict(zip(keys, values))


async def async_get_text_changes(
    *,
    name: str | None = None,
    node: str | None = None,
) -> spec.DataFrame:

    event_abi: spec.EventABI = {
        'name': 'TextChanged',
        'type': 'event',
        'inputs': [
            {
                'indexed': True,
                'internalType': 'bytes32',
                'name': 'node',
                'type': 'bytes32',
            },
            {
                'indexed': True,
                'internalType': 'string',
                'name': 'indexedKey',
                'type': 'string',
            },
            {
                'indexed': False,
                'internalType': 'string',
                'name': 'key',
                'type': 'string',
            },
        ],
    }

    events = await evm.async_get_events(
        contract_address=ens_directory.resolver,
        event_abi=event_abi,
        start_block=9000000,
        verbose=False,
    )

    if node is None:
        if name is None:
            raise Exception('must specify name or node')
        node = hash_name(name)

    mask = events['arg__node'] == node
    return events[mask]


async def async_get_content_hash(
    name: str | None = None,
    node: str | None = None,
) -> str:

    if node is None:
        if name is None:
            raise Exception('must specify name or node')
        node = hash_name(name)

    function_abi: spec.FunctionABI = {
        'name': 'contenthash',
        'inputs': [
            {'name': 'node', 'type': 'bytes32'},
        ],
        'outputs': [{'name': '', 'type': 'bytes'}],
    }

    result = await rpc.async_eth_call(
        to_address=ens_directory.resolver,
        function_abi=function_abi,
        function_parameters=[node],
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


async def async_get_expiration(name: str) -> int:

    if not name.endswith('.eth'):
        raise NotImplementedError('only implemented for .eth domains')

    label = name.split('.')[-2]
    label_id = evm.keccak_text(label, output_format='integer')

    function_abi: spec.FunctionABI = {
        'name': 'nameExpires',
        'inputs': [{'name': 'id', 'type': 'uint256'}],
        'outputs': [{'type': 'uint256'}],
    }

    result = await rpc.async_eth_call(
        to_address=ens_directory.base_registrar,
        function_abi=function_abi,
        function_parameters=[label_id],
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result
