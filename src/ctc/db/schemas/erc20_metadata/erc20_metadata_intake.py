from __future__ import annotations

from ctc import spec
from .. import connect_utils
from . import erc20_metadata_statements


async def async_intake_erc20_metadata(
    address: spec.Address,
    network: spec.NetworkReference,
    *,
    decimals: int | None = None,
    symbol: str | None = None,
    name: str | None = None,
) -> None:

    engine = connect_utils.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return
    with engine.begin() as conn:
        await erc20_metadata_statements.async_upsert_erc20_metadata(
            conn=conn,
            network=network,
            address=address,
            decimals=decimals,
            symbol=symbol,
            name=name,
        )
