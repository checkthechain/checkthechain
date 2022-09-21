# TODO: update with additional proxy types, see:
# - https://github.com/ApeWorX/ape/pull/750
# - https://docs.openzeppelin.com/contracts/4.x/api/proxy

from __future__ import annotations

import typing

from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict, Literal

    class ProxyAddressMetadata(TypedDict):
        implementation: spec.Address | None
        proxy_type: Literal[
            'eip897',
            'eip1967-logic',
            'eip1967-beacon',
            'openzeppelin',
            'gnosis_safe',
        ] | None


async def async_get_proxy_implementation(
    contract_address: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address | None:
    """return implementation address of proxy contract"""

    proxy_metadata = await async_get_proxy_metadata(
        contract_address=contract_address, provider=provider, block=block
    )

    return proxy_metadata['implementation']


async def async_get_proxy_metadata(
    contract_address: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> ProxyAddressMetadata:
    """return metadata of proxy address"""

    # try eip897
    try:
        eip897_address = await _async_get_eip897_implementation(
            contract_address=contract_address,
            provider=provider,
            block=block,
        )
        if eip897_address is not None:
            return {
                'implementation': eip897_address,
                'proxy_type': 'eip897',
            }
    except (spec.exceptions.rpc_exceptions.RpcException, Exception):
        pass

    # try eip1967 logic
    eip1967_logic_address = await _async_get_eip1967_proxy_logic_address(
        contract_address=contract_address,
        provider=provider,
        block=block,
    )
    if eip1967_logic_address != '0x0000000000000000000000000000000000000000':
        return {
            'implementation': eip1967_logic_address,
            'proxy_type': 'eip1967-logic',
        }

    # try eip1967 beacon
    eip1967_beacon_address = await _async_get_eip1967_proxy_beacon_address(
        contract_address=contract_address,
        provider=provider,
        block=block,
    )
    if eip1967_beacon_address is not None:
        return {
            'implementation': eip1967_beacon_address,
            'proxy_type': 'eip1967-beacon',
        }

    # try openzeppelin
    openzeppelin_address = await _async_get_oz_proxy_address(
        contract_address=contract_address,
        provider=provider,
        block=block,
    )
    if openzeppelin_address is not None:
        return {
            'implementation': openzeppelin_address,
            'proxy_type': 'openzeppelin',
        }

    # try gnosis proxy
    gnosis_proxy_address = await _async_get_gnosis_safe_proxy_address(
        contract_address,
        provider=provider,
        block=block,
    )
    if gnosis_proxy_address is not None:
        return {
            'implementation': gnosis_proxy_address,
            'proxy_type': 'gnosis_safe',
        }

    return {
        'implementation': None,
        'proxy_type': None,
    }


#
# # eip897
#


async def _async_get_eip897_proxy_type(
    contract_address: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> int | None:

    from ctc import rpc

    function_abi: spec.FunctionABI = {
        'name': 'proxyType',
        'type': 'function',
        'inputs': [],
        'outputs': [
            {'name': 'proxyTypeId', 'type': 'uint256'},
        ],
    }

    result = await rpc.async_eth_call(
        to_address=contract_address,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )
    if result is not None and not isinstance(result, int):
        raise Exception('invalid rpc result')
    return result


async def _async_get_eip897_implementation(
    contract_address: spec.Address,
    *,
    provider: spec.ProviderReference = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address:

    from ctc import rpc

    function_abi: spec.FunctionABI = {
        'name': 'implementation',
        'type': 'function',
        'inputs': [],
        'outputs': [
            {'name': 'codeAddr', 'type': 'address'},
        ],
    }

    result = await rpc.async_eth_call(
        to_address=contract_address,
        function_abi=function_abi,
        provider=provider,
        block_number=block,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')
    return result


#
# # eip1967
#


async def _async_get_eip1967_proxy_logic_address(
    contract_address: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> spec.Address:
    """get a contract's logic address

    storage position obtained as:
        bytes32(uint256(keccak256('eip1967.proxy.implementation')) - 1)

    see https://eips.ethereum.org/EIPS/eip-1967
    """

    from ctc import rpc

    position = (
        '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')

    return '0x' + result[-40:]


async def _async_get_eip1967_proxy_beacon_address(
    contract_address: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> spec.Address | None:
    """get a contract's logic address

    storage position obtained as:
        bytes32(uint256(keccak256('eip1967.proxy.beacon')) - 1)

    see https://eips.ethereum.org/EIPS/eip-1967
    """

    from ctc import rpc

    position = (
        '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')

    beacon = '0x' + result[-40:]
    if beacon == '0x0000000000000000000000000000000000000000':
        return None

    implementation_abi: spec.FunctionABI = {
        'name': 'implementation',
        'type': 'function',
        'inputs': [],
        'outputs': [{'type': 'address'}],
    }

    try:
        proxy_in_beacon = await rpc.async_eth_call(
            to_address=beacon,
            function_abi=implementation_abi,
            provider=provider,
        )
    except Exception:
        proxy_in_beacon = None

    if not isinstance(proxy_in_beacon, str):
        raise Exception('bad rpc data')
    return proxy_in_beacon


async def _async_get_eip1967_proxy_admin_address(
    contract_address: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> spec.Address:
    """get a contract's logic address

    storage position obtained as:
        bytes32(uint256(keccak256('eip1967.proxy.admin')) - 1)

    see https://eips.ethereum.org/EIPS/eip-1967
    """

    from ctc import rpc

    position = (
        '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')

    return '0x' + result[-40:]


# async def async_get_eip1967_history() -> None:
#     raise NotImplementedError(
#         'use events here, see https://docs.openzeppelin.com/contracts/4.x/api/proxy#BeaconProxy'
#     )


#
# # openzeppelin os
#


async def _async_get_oz_proxy_address(
    contract_address: spec.Address,
    *,
    block: typing.Optional[spec.BlockNumberReference] = None,
    provider: spec.ProviderReference = None,
) -> spec.Address | None:

    from ctc import rpc

    position = (
        '0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c036e5a723fd8ee048ed3f8c3'
    )

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position=position,
        block_number=block,
        provider=provider,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')

    address = '0x' + result[-40:]

    if address == '0x0000000000000000000000000000000000000000':
        return None
    else:
        return address


#
# # gnosis
#


async def _async_get_gnosis_safe_proxy_address(
    contract_address: spec.Address,
    *,
    block: spec.BlockNumberReference | None = None,
    confirm_bytecode: bool = True,
    provider: spec.ProviderReference = None,
) -> spec.Address | None:

    from ctc import rpc

    if confirm_bytecode:
        gnosis_proxy_code = '0x608060405273ffffffffffffffffffffffffffffffffffffffff600054167fa619486e0000000000000000000000000000000000000000000000000000000060003514156050578060005260206000f35b3660008037600080366000845af43d6000803e60008114156070573d6000fd5b3d6000f3fea2646970667358221220d1429297349653a4918076d650332de1a1068c5f3e07c5c82360c277770b955264736f6c63430007060033'
        bytecode = await rpc.async_eth_get_code(
            contract_address, block_number=block
        )
        if bytecode != gnosis_proxy_code:
            return None

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position='0x0',
        provider=provider,
        block_number=block,
    )
    if not isinstance(result, str):
        raise Exception('invalid rpc result')

    return '0x' + result[-40:]
