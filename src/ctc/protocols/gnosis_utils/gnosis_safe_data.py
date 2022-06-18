from __future__ import annotations

import asyncio
import typing

import toolstr

from ctc import evm
from ctc import rpc
from ctc import spec


function_abis = {
    'getOwners': {
        'inputs': [],
        'name': 'getOwners',
        'outputs': [
            {'internalType': 'address[]', 'name': '', 'type': 'address[]'}
        ],
        'stateMutability': 'view',
        'type': 'function',
    },
    'getThreshold': {
        'inputs': [],
        'name': 'getThreshold',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
    'nonce': {
        'inputs': [],
        'name': 'nonce',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view',
        'type': 'function',
    },
}


async def async_get_safe_owners(
    address: spec.Address,
) -> typing.Sequence[spec.Address]:
    return await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abis['getOwners'],
    )


async def async_get_safe_threshold(address: spec.Address) -> int:
    return await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abis['getThreshold'],
    )


async def async_get_safe_nonce(address: spec.Address) -> int:
    return await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abis['nonce'],
    )


async def async_print_safe_summary(address: spec.Address) -> None:
    import tooltime

    owners_coroutine = async_get_safe_owners(address)
    threshold_coroutine = async_get_safe_threshold(address)
    nonce_coroutine = async_get_safe_nonce(address)
    creation_block_coroutine = evm.async_get_contract_creation_block(address)

    owners, threshold, nonce, creation_block = await asyncio.gather(
        owners_coroutine,
        threshold_coroutine,
        nonce_coroutine,
        creation_block_coroutine,
    )

    creation_timestamp = await evm.async_get_block_timestamp(creation_block)
    age = tooltime.get_age(creation_timestamp, 'TimelengthPhrase')

    toolstr.print_text_box('Gnosis Safe ' + str(address))
    print('- threshold:', threshold, '/', len(owners))
    print('- owners:')
    for owner in owners:
        print('    -', owner)
    print('- nonce:', nonce)
    print('- creation block:', creation_block)
    print(
        '- creation date:', tooltime.timestamp_to_iso_pretty(creation_timestamp)
    )
    print('- age:', age)
