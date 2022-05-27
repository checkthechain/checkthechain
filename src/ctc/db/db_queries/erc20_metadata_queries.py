from __future__ import annotations

import typing

from ctc import spec

from .. import db_connect
from .. import db_statements
from .. import db_spec


async def async_query_erc20_metadata(
    address: spec.Address,
    network: spec.NetworkReference,
) -> db_spec.ERC20Metadata | None:
    engine = db_connect.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await db_statements.async_select_erc20_metadata(
            conn=conn,
            address=address,
            network=network,
        )


async def async_query_erc20s_metadata(
    addresses: spec.Address,
    network: spec.NetworkReference,
) -> typing.Sequence[db_spec.ERC20Metadata | None]:
    engine = db_connect.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return [None] * len(addresses)
    with engine.connect() as conn:
        return await db_statements.async_select_erc20_metadatas(
            conn=conn,
            addresses=addresses,
            network=network,
        )
