# https://docs.chain.link/docs/faq/

import typing
from typing_extensions import TypedDict

from ctc import spec


_FeedReference = typing.Union[spec.Address, str]


class FeedRoundData(TypedDict):
    answer: int
    round_id: int
    timestamp: int


class FeedRoundDataNormalized(TypedDict):
    answer: float
    round_id: int
    timestamp: int


path_templates = {
    'feed': '{chainlink_view}/feeds/{feed}/{feed}__{start_block}_to_{end_block}.csv',
}

