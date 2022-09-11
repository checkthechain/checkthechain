from __future__ import annotations

import typing

from ctc import spec


def get_dex_names_of_factories(
    network: spec.NetworkReference,
) -> typing.Mapping[spec.Address, str]:
    """get mapping of factory_address -> dex_name"""

    if network in (1, 'mainnet'):
        return {
            '0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f': 'Uniswap V2',
            '0x1f98431c8ad98523631ae4a59f267346ea31f984': 'Uniswap V3',
            '0xba12222222228d8ba445958a75a0704d566bf2c8': 'Balancer',
            '0xb9fc157394af804a3578134a6585c0dc9cc990d4': 'Curve',
            '0x0959158b6040d32d04c301a72cbfd6b39e21c9ae': 'Curve',
            '0xf18056bbd320e96a48e3fbf8bc061322531aac99': 'Curve',
            '0x90e00ace148ca3b23ac1bc8c240c2a7dd9c2d7f5': 'Curve',
            '0x8f942c20d02befc377d41445793068908e2250d0': 'Curve',
            '0xbabe61887f1de2713c6f97e567623453d3c79f67': 'Curve',
            '0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac': 'Sushi',
        }
    else:
        raise Exception(
            'dex pool factory map not available for network: ' + str(network)
        )


def get_dex_name_of_factory(
    factory: spec.Address,
    network: spec.NetworkReference,
) -> str:
    """get dex_name of factory address"""

    names_of_factories = get_dex_names_of_factories(network=network)
    return names_of_factories[factory]
