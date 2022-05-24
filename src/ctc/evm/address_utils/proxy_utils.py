from __future__ import annotations

import typing

from ctc import rpc
from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict, Literal

    class ProxyAddressMetadata(TypedDict):
        address: spec.Address | None
        proxy_type: Literal['eip897', 'eip1967', 'gnosis_safe'] | None


async def async_get_proxy_address(
    contract_address: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference | None = None,
) -> spec.Address | None:

    proxy_metadata = await async_get_proxy_metadata(
        contract_address=contract_address,
        provider=provider,
        block=block
    )

    return proxy_metadata['address']


async def async_get_proxy_metadata(
    contract_address: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference | None = None,
) -> ProxyAddressMetadata:
    # try eip897
    try:
        eip897_address = await _async_get_eip897_implementation(
            contract_address=contract_address,
            provider=provider,
            block=block,
        )
        if eip897_address is not None:
            return {
                'address': eip897_address,
                'proxy_type': 'eip897',
            }
    except (spec.exceptions.rpc_exceptions.RpcException, Exception):
        pass

    # try eip1967
    eip1967_address = await _async_get_eip1967_proxy_logic_address(
        contract_address=contract_address,
        provider=provider,
        block=block,
    )
    if eip1967_address != '0x0000000000000000000000000000000000000000':
        return {
            'address': eip1967_address,
            'proxy_type': 'eip1967',
        }

    # try gnosis proxy
    gnosis_proxy_address = await async_get_gnosis_safe_proxy_address(
        contract_address,
        provider=provider,
        block=block,
    )
    if gnosis_proxy_address is not None:
        return {
            'address': gnosis_proxy_address,
            'proxy_type': 'gnosis_safe',
        }

    return {
        'address': None,
        'proxy_type': None,
    }


#
# # eip897
#


async def _async_get_eip897_proxy_type(
    contract_address: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference | None = None,
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
        block_number=block,
    )


async def _async_get_eip897_implementation(
    contract_address: spec.Address,
    provider: spec.ProviderSpec = None,
    block: spec.BlockNumberReference | None = None,
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
        block_number=block,
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
    provider: spec.ProviderSpec = None,
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
        provider=provider,
    )

    return '0x' + result[-40:]


async def async_get_eip1967_history() -> None:
    raise NotImplementedError('use events here, see https://docs.openzeppelin.com/contracts/4.x/api/proxy#BeaconProxy')


#
# # gnosisc
#


async def async_get_gnosis_safe_proxy_address(
    contract_address: spec.Address,
    block: spec.BlockNumberReference | None = None,
    confirm_bytecode: bool = True,
    provider: spec.ProviderSpec = None,
) -> spec.Address | None:

    if confirm_bytecode:
        gnosis_proxy_code = '0x608060405273ffffffffffffffffffffffffffffffffffffffff600054167fa619486e0000000000000000000000000000000000000000000000000000000060003514156050578060005260206000f35b3660008037600080366000845af43d6000803e60008114156070573d6000fd5b3d6000f3fea2646970667358221220d1429297349653a4918076d650332de1a1068c5f3e07c5c82360c277770b955264736f6c63430007060033'
        bytecode = await rpc.async_eth_get_code(contract_address, block_number=block)
        if bytecode != gnosis_proxy_code:
            return None

    result = await rpc.async_eth_get_storage_at(
        address=contract_address,
        position='0x0',
        provider=provider,
        block_number=block,
    )

    return '0x' + result[-40:]
