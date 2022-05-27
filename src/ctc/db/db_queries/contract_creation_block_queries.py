from __future__ import annotations

from ctc import spec

from .. import db_connect
from .. import db_statements


async def async_query_contract_creation_block(
    address: spec.Address,
    network: spec.NetworkReference,
) -> int | None:
    engine = db_connect.create_engine(
        schema_name='contract_creation_blocks',
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await db_statements.async_select_contract_creation_block(
            conn=conn,
            address=address,
            network=network,
        )
