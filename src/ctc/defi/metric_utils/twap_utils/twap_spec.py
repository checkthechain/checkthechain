from __future__ import annotations

import typing

from ctc import spec

if typing.TYPE_CHECKING:
    from typing_extensions import TypedDict

    class DataSource(TypedDict, total=False):
        protocol: typing.Literal['UniswapV2', 'Chainlink']
        feed: typing.Union[str, spec.Address]
        composite_feed: typing.Union[str, spec.Address]
        invert: bool
        normalize: bool
        mode: typing.Literal['native', 'raw']

