import typing

from ctc import directory
from ctc import rpc
from ctc import spec
from . import abi_utils


eip_897_abi = [
    {
        'name': 'proxyType',
        'type': 'function',
        'inputs': [],
        'outputs': [
            {'name': 'proxyTypeId', 'type': 'uint256'},
        ],
    },
    {
        'name': 'implementation',
        'type': 'function',
        'inputs': [],
        'outputs': [
            {'name': 'codeAddr', 'type': 'address'},
        ],
    },
]


async def async_get_eip897_proxy_type(
    contract_address: spec.Address, provider: spec.ProviderSpec = None
) -> int:

    function_abi = eip_897_abi[0]
    assert function_abi['name'] == 'proxyType'

    return await rpc.async_eth_call(
        to_address=contract_address,
        function_abi=function_abi,
        provider=provider,
    )


async def async_get_eip897_implementation(
    contract_address: spec.Address, provider: spec.ProviderSpec = None
) -> spec.Address:

    function_abi = eip_897_abi[1]
    assert function_abi['name'] == 'implementation'

    return await rpc.async_eth_call(
        to_address=contract_address,
        function_abi=function_abi,
        provider=provider,
    )


async def async_get_eip1967_proxy_logic_address(
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


async def async_save_eip897_abi(
    contract_address: spec.Address, provider: spec.ProviderSpec = None
) -> None:

    provider = rpc.get_provider(provider)
    eip897_address = await async_get_eip897_implementation(
        contract_address,
        provider=provider,
    )

    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    abi_utils.async_save_proxy_contract_abi_to_filesystem(
        contract_address=contract_address,
        proxy_implementation=eip897_address,
        network=network,
    )


async def async_get_eip1967_proxy_beacon_address(
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


async def async_get_eip1967_proxy_admin_address(
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

