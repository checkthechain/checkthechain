from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ctc.protocols import uniswap_v2_utils
from . import sushi_spec


async def async_get_pools(
    *,
    assets: typing.Sequence[spec.Address] | None = None,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    factory: spec.Address | None = None,
    update: bool = False,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference | None = None,
) -> typing.Sequence[spec.DexPool]:

    network, provider = evm.get_network_and_provider(network, provider)

    if factory is None:
        network, provider = evm.get_network_and_provider(network, provider)
        if network not in (1, 'mainnet'):
            raise Exception(
                'sushi factory unknown for network: ' + str(network)
            )
        factory = sushi_spec.get_sushiswap_factory(network)

    return await uniswap_v2_utils.async_get_pools(
        assets=assets,
        start_block=start_block,
        end_block=end_block,
        factory=factory,
        update=update,
        network=network,
        provider=provider,
    )
