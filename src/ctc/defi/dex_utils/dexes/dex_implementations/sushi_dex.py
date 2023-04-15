from __future__ import annotations

from . import uniswap_v2_dex


class SushiDEX(uniswap_v2_dex.UniswapV2DEX):
    """Sushi DEX"""

    _pool_factories = {1: ['0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac']}
