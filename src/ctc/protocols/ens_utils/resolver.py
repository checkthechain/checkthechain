from ctc import binary
from ctc import rpc

from . import ens_directory
from . import registrar


def hash_name(name):
    import idna

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

