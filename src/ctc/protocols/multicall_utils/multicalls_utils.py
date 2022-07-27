"""
Maker multicall
- https://github.com/makerdao/multicall

Uniswap V3 multicall
- https://docs.uniswap.org/protocol/reference/periphery/base/Multicall
- https://github.com/Uniswap/v3-periphery/blob/main/contracts/base/Multicall.sol
"""

from __future__ import annotations

import asyncio
import typing

from ctc import evm
from ctc import spec
from ctc import rpc
from . import call_utils
from . import multicall_spec


function_abis: typing.Mapping[str, spec.FunctionABI] = {
    'aggregate': {
        'inputs': [
            {
                'components': [
                    {'name': 'target', 'type': 'address'},
                    {'name': 'callData', 'type': 'bytes'},
                ],
                'name': 'calls',
                'type': 'tuple[]',
            }
        ],
        'name': 'aggregate',
        'outputs': [
            {'name': 'blockNumber', 'type': 'uint256'},
            {'name': 'returnData', 'type': 'bytes[]'},
        ],
        'stateMutability': 'nonpayable',
        'type': 'function',
    }
}


def get_multicall_address(
    *,
    network: spec.NetworkReference = 'mainnet',
    version: str = 'maker',
) -> spec.Address:

    network_name = evm.get_network_name(network, require=True)

    if version.lower() == 'Maker'.lower():
        multicall = {
            'mainnet': '0xeefba1e63905ef1d7acba5a8513c70307c1ce441',
            'kovan': '0x2cc8688c5f75e365aaeeb4ea8d6a480405a48d2a',
            'rinkeby': '0x42ad527de7d4e9d9d011ac45b31d8551f8fe9821',
            'gorli': '0x77dca2c955b15e9de4dbbcf1246b4b85b651e50e',
            'ropsten': '0x53c43764255c17bd724f74c4ef150724ac50a3ed',
            'xdai': '0xb5b692a88bdfc81ca69dcb1d924f59f0413a602a',
            'polygon': '0x11ce4b23bd875d7f5c6a31084f55fde1e9a87507',
            'mumbai': '0x08411add0b5aa8ee47563b146743c13b3556c9cc',
        }
        return multicall[network_name]
    elif version.lower() == 'Uniswap V3':
        # same across networks
        return '0x5ba1e12693dc8f9c48aad8770482f4739beed696'
    else:
        raise Exception('unknown version: ' + str(version))


async def async_multicall(
    calls: typing.Sequence[multicall_spec.Call],
    *,
    block: spec.BlockNumberReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.List[typing.Any]:

    network = rpc.get_provider_network(provider)

    # encode calls
    coroutines = [
        call_utils.async_encode_call(call, network=network) for call in calls
    ]
    encoded_calls = await asyncio.gather(*coroutines)

    # get multicall contract address
    multicall_address = get_multicall_address(network=network)

    # make call
    results = await rpc.async_eth_call(
        to_address=multicall_address,
        function_abi=function_abis['aggregate'],
        function_parameters=[encoded_calls],
        block_number=block,
        provider=provider,
    )
    block_number, encoded_outputs = results

    # decode outputs
    coroutines = [
        call_utils.async_decode_call_output(
            call=call,
            encoded_output=encoded_output,
            network=network,
        )
        for call, encoded_output in zip(calls, encoded_outputs)
    ]
    decoded_outputs = await asyncio.gather(*coroutines)

    return decoded_outputs


async def async_multicall_by_block(
    calls: typing.Sequence[multicall_spec.Call],
    *,
    blocks: typing.Sequence[spec.BlockNumberReference],
    provider: spec.ProviderReference = None,
) -> typing.Sequence[typing.Sequence[typing.Any]]:
    coroutines = [
        async_multicall(
            calls=calls,
            block=block,
            provider=provider,
        )
        for block in blocks
    ]
    results = asyncio.gather(*coroutines)
    return list(zip(*results))
