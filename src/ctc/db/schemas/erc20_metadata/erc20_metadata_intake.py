from __future__ import annotations

import toolsql

from ctc import spec
from . import erc20_metadata_statements


async def async_intake_erc20_metadata(
    address: spec.Address,
    *,
    context: spec.Context,
    decimals: int | None = None,
    symbol: str | None = None,
    name: str | None = None,
) -> None:

    from ctc import config

    db_config = config.get_context_db_config(
        schema_name='erc20_metadata',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        await erc20_metadata_statements.async_upsert_erc20_metadata(
            conn=conn,
            address=address,
            decimals=decimals,
            symbol=symbol,
            name=name,
            context=context,
        )
