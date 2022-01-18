# https://docs.chain.link/docs/faq/

import typing

from ctc import spec


_FeedReference = typing.Union[spec.Address, str]


class FeedRoundData(typing.TypedDict):
    roundId: int
    answer: typing.Union[int, float]
    startedAt: int
    updatedAt: int
    answeredInRound: int


class FeedRoundDataNormalized(typing.TypedDict):
    roundId: int
    answer: float
    startedAt: int
    updatedAt: int
    answeredInRound: int


path_templates = {
    'feed': '{chainlink_view}/feeds/{feed}/{feed}__{start_block}_to_{end_block}.csv',
}

