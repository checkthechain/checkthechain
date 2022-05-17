from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec


async def async_get_proxy_address(
    contract_address: spec.Address,
    provider: spec.ProviderSpec = None,
) -> spec.Address | None:

    # try eip897
    try:
        eip897_address = await _async_get_eip897_implementation(
            contract_address=contract_address,
            provider=provider,
        )
        if eip897_address is not None:
            return eip897_address
    except spec.exceptions.rpc_exceptions.RpcException:
        pass

    # try eip1967
    eip1967_address = await _async_get_eip1967_proxy_logic_address(
        contract_address=contract_address,
        provider=provider,
    )
    if eip1967_address != '0x0000000000000000000000000000000000000000':
        return eip1967_address

    return None


#
# # eip897
#


async def _async_get_eip897_proxy_type(
    contract_address: spec.Address, provider: spec.ProviderSpec = None
) -> int | None:

    function_abi: spec.FunctionABI = {
        'name': 'proxyType',
        'type': 'function',
        'inputs': [],
        'outputs': [
            {'name': 'proxyTypeId', 'type': 'uint256'},
        ],
    }

    return await rpc.async_eth_call(
        to_address=contract_address,
        function_abi=function_abi,
        provider=provider,
    )


async def _async_get_eip897_implementation(
    contract_address: spec.Address, provider: spec.ProviderSpec = None
) -> spec.Address:

    function_abi: spec.FunctionABI = {
        'name': 'implementation',
        'type': 'function',
        'inputs': [],
        'outputs': [
            {'name': 'codeAddr', 'type': 'address'},
        ],
    }

    return await rpc.async_eth_call(
        to_address=contract_address,
        function_abi=function_abi,
        provider=provider,
    )


#
# # eip1967
#


async def _async_get_eip1967_proxy_logic_address(
    contract_address: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderSpec = None,
) -> spec.Address:
    """get a contract's logic address

    storage position obtained as:
        bytes32(uint256(keccak256('eip1967.proxy.implementation')) - 1)

    see https://eips.ethereum.org/EIPS/eip-1967
    """

    position = (
        '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
        provider=provider,
    )

    return '0x' + result[-40:]


async def _async_get_eip1967_proxy_beacon_address(
    contract_address: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> spec.Address:
    """get a contract's logic address

    storage position obtained as:
        bytes32(uint256(keccak256('eip1967.proxy.beacon')) - 1)

    see https://eips.ethereum.org/EIPS/eip-1967
    """

    position = (
        '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
    )

    return '0x' + result[-40:]


async def _async_get_eip1967_proxy_admin_address(
    contract_address: spec.Address,
    block: typing.Optional[spec.BlockNumberReference] = None,
) -> spec.Address:
    """get a contract's logic address

    storage position obtained as:
        bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1)

    see https://eips.ethereum.org/EIPS/eip-1967
    """

    position = (
        '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
    )

    return '0x' + result[-40:]
