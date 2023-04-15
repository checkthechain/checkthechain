from __future__ import annotations

import typing
from typing_extensions import TypedDict

from ctc import spec


class DataSource(TypedDict, total=False):
    protocol: typing.Literal['UniswapV2', 'Chainlink']
    feed: typing.Union[str, spec.Address]
    composite_feed: typing.Union[str, spec.Address]
    invert: bool
    normalize: bool
    mode: typing.Literal['native', 'raw']
