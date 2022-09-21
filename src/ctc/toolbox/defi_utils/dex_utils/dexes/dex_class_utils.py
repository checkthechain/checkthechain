"""functions for getting dex classes"""

from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from . import dex_directory
from . import dex_class


def get_all_dex_classes() -> typing.Mapping[str, typing.Type[dex_class.DEX]]:
    """get all DEX classes"""
    dex_names = [
        'balancer',
        'curve',
        'sushi',
        'uniswapv2',
        'uniswapv3',
    ]
    return {dex_name: get_dex_class(dex_name) for dex_name in dex_names}


def get_dex_class(
    dex: typing.Type[dex_class.DEX] | str | None = None,
    *,
    factory: spec.Address | None = None,
    network: spec.NetworkReference | None = None,
) -> typing.Type[dex_class.DEX]:
    """return DEX object corresponding to dex name or dex factory"""

    if dex is not None:
        if isinstance(dex, str):
            return _get_dex_class_from_name(dex)
        elif issubclass(dex, dex_class.DEX):
            return dex
        else:
            raise Exception('unknown dex type: ' + str(type(dex)))
    elif factory is not None:
        return _get_dex_class_from_factory(factory=factory, network=network)
    else:
        raise Exception('not enough inputs specified')


async def async_get_dex_class(
    dex: typing.Type[dex_class.DEX] | str | None = None,
    *,
    factory: spec.Address | None = None,
    pool: spec.Address | None = None,
    network: spec.NetworkReference | None = None,
    provider: spec.ProviderReference = None,
) -> typing.Type[dex_class.DEX]:
    """get DEX class matching given inputs"""

    network, provider = evm.get_network_and_provider(network, provider)
    if factory is not None or dex is not None:
        return get_dex_class(
            dex=dex,
            factory=factory,
            network=network,
        )
    else:
        if pool is None:
            raise Exception(
                'must specify dex, factory or pool to get dex class'
            )
        return await _async_get_dex_class_of_pool(pool, network=network)


def _get_dex_class_from_factory(
    factory: spec.Address,
    network: spec.NetworkReference | None,
) -> typing.Type[dex_class.DEX]:
    """return DEX class using given DEX factory"""

    if network is None:
        raise Exception('must specify network of factory')
    dex_name = dex_directory.get_dex_name_of_factory(factory, network=network)
    return _get_dex_class_from_name(dex_name)


def _get_dex_class_from_name(dex: str) -> typing.Type[dex_class.DEX]:
    """return DEX class using given DEX name"""

    dex = dex.lower().replace(' ', '').replace('-', '').replace('_', '')

    if dex == 'balancer':
        from .dex_implementations import balancer_dex

        return balancer_dex.BalancerDEX
    elif dex == 'curve':
        from .dex_implementations import curve_dex

        return curve_dex.CurveDEX
    elif dex == 'sushi':
        from .dex_implementations import sushi_dex

        return sushi_dex.SushiDEX
    elif dex == 'uniswapv2':
        from .dex_implementations import uniswap_v2_dex

        return uniswap_v2_dex.UniswapV2DEX
    elif dex == 'uniswapv3':
        from .dex_implementations import uniswap_v3_dex

        return uniswap_v3_dex.UniswapV3DEX
    else:
        raise Exception('unknown DEX: ' + str(dex))


async def _async_get_dex_class_of_pool(
    pool: spec.Address,
    network: spec.NetworkReference | None,
) -> typing.Type[dex_class.DEX]:
    """get DEX class for given pool"""

    from ctc import db

    dex_pool = await db.async_query_dex_pool(address=pool, network=network)
    if dex_pool is None:
        raise Exception('could not determine dex class of pool')
    return _get_dex_class_from_factory(dex_pool['factory'], network=network)
