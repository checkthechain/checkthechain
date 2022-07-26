from __future__ import annotations

import typing

from ctc import db
from .. import market_utils
from . import coingecko_schema_defs
from . import coingecko_statements


async def async_intake_tokens(
    tokens: typing.Sequence[coingecko_schema_defs.CoingeckoToken],
    n_ranked: int = 500,
) -> None:

    # add rank data
    market_data = await market_utils.async_get_market_data(n_ranked)
    ranks_of_symbols = {
        item['id']: item['market_cap_rank'] for item in market_data
    }
    for token in tokens:
        rank = ranks_of_symbols.get(token['id'])
        if rank is not None:
            token['market_cap_rank'] = rank

    # add to db
    engine = db.create_engine(
        schema_name='coingecko',
        network=None,
    )
    if engine is None:
        return
    with engine.begin() as conn:
        await coingecko_statements.async_upsert_tokens(
            tokens=tokens,
            conn=conn,
        )
