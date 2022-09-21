from __future__ import annotations

import typing

from ctc import spec


async def async_is_contract_address(
    address: spec.Address,
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderReference = None,
) -> bool:
    """return whether address has bytecode on chain"""

    from ctc import rpc

    code = await rpc.async_eth_get_code(
        address=address,
        block_number=block,
        provider=provider,
    )
    return len(code) >= 3


async def async_are_contract_addresses(
    addresses: typing.Sequence[spec.Address],
    *,
    block: spec.BlockNumberReference = 'latest',
    provider: spec.ProviderReference = None,
) -> dict[spec.Address, bool]:
    """return whether addresses have bytecode on chain"""

    from ctc import rpc

    codes = await rpc.async_batch_eth_get_code(
        addresses=addresses,
        block_number=block,
        provider=provider,
    )
    return {address: len(code) > 3 for address, code in zip(addresses, codes)}
