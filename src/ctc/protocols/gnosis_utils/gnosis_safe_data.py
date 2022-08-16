from __future__ import annotations

import asyncio
import typing

import toolstr

from ctc import evm
from ctc import rpc
from ctc import spec


function_abis: typing.Mapping[str, spec.FunctionABI] = {
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
    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abis['getOwners'],
    )
    if not isinstance(result, (tuple, list)) or not all(
        isinstance(item, str) for item in result
    ):
        raise Exception('invalid rpc result')
    return result


async def async_get_safe_threshold(address: spec.Address) -> int:
    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abis['getThreshold'],
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_get_safe_nonce(address: spec.Address) -> int:
    result = await rpc.async_eth_call(
        to_address=address,
        function_abi=function_abis['nonce'],
    )
    if not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def async_print_safe_summary(
    address: spec.Address, verbose: bool = False
) -> None:
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

    if creation_block is not None:
        creation_timestamp = await evm.async_get_block_timestamp(creation_block)
        creation_date = tooltime.timestamp_to_iso_pretty(creation_timestamp)
        age = tooltime.get_age(creation_timestamp, 'TimelengthPhrase')
    else:
        creation_timestamp = None
        creation_date = None
        age = None

    toolstr.print_text_box('Gnosis safe ' + str(address))
    print('- threshold:', threshold, '/', len(owners))
    print('- owners:')
    for owner in owners:
        print('    -', owner)
    print('- nonce:', nonce)
    print('- creation block:', creation_block)
    print('- creation date:', creation_date)
    print('- age:', age)

    if verbose:
        default_erc20s = await evm.async_get_default_erc20_tokens()
        erc20_addresses = [default['address'] for default in default_erc20s]

        print()
        toolstr.print_text_box('Common ERC20s in safe')
        balances = await evm.async_get_erc20s_balances(
            wallet=address,
            tokens=erc20_addresses,
        )

        rows = []
        for erc20, balance in zip(default_erc20s, balances):
            if balance > 0:
                row = [erc20['symbol'], balance]
                rows.append(row)
        labels = ['token', 'balance']
        if len(rows) == 0:
            print('[none]')
        else:
            toolstr.print_table(rows, labels=labels)
