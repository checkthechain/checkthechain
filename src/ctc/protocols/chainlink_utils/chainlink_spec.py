# https://docs.chain.link/docs/faq/

import typing

from ctc import spec


_FeedReference = typing.Union[spec.Address, str]


class FeedRoundData(typing.TypedDict):
    answer: int
    round_id: int
    timestamp: int


class FeedRoundDataNormalized(typing.TypedDict):
    answer: float
    round_id: int
    timestamp: int


path_templates = {
    'feed': '{chainlink_view}/feeds/{feed}/{feed}__{start_block}_to_{end_block}.csv',
}

