from __future__ import annotations

import typing

from ctc import spec
from . import dex_directory
from . import dex_class


def get_dex(
    dex: typing.Type[dex_class.DEX] | str | None = None,
    *,
    factory: spec.Address | None = None,
    network: spec.NetworkReference | None = None,
) -> typing.Type[dex_class.DEX]:
    """return DEX object corresponding to dex name or dex factory"""

    if dex is not None:
        if isinstance(dex, str):
            return get_dex_by_name(dex)
        elif issubclass(dex, dex_class.DEX):
            return dex
        else:
            raise Exception('unknown dex type: ' + str(type(dex)))
    elif factory is not None:
        return get_dex_by_factory(factory=factory, network=network)
    else:
        raise Exception('not enough inputs specified')


def get_dex_by_factory(
    factory: spec.Address,
    network: spec.NetworkReference | None,
) -> typing.Type[dex_class.DEX]:
    """return DEX class using given DEX factory"""

    if network is None:
        raise Exception('must specify network of factory')
    dex_name = dex_directory.get_dex_name_of_factory(factory, network=network)
    return get_dex_by_name(dex_name)


def get_dex_by_name(dex: str) -> typing.Type[dex_class.DEX]:
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
