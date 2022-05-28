from __future__ import annotations

import typing

from ctc import spec

from ... import connect_utils
from . import erc20_metadata_schema_defs
from . import erc20_metadata_statements


async def async_query_erc20_metadata(
    address: spec.Address,
    network: spec.NetworkReference,
) -> erc20_metadata_schema_defs.ERC20Metadata | None:
    engine = connect_utils.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await erc20_metadata_statements.async_select_erc20_metadata(
            conn=conn,
            address=address,
            network=network,
        )


async def async_query_erc20s_metadata(
    addresses: spec.Address,
    network: spec.NetworkReference,
) -> typing.Sequence[erc20_metadata_schema_defs.ERC20Metadata | None]:
    engine = connect_utils.create_engine(
        schema_name='erc20_metadata',
        network=network,
    )
    if engine is None:
        return [None] * len(addresses)
    with engine.connect() as conn:
        return await erc20_metadata_statements.async_select_erc20_metadatas(
            conn=conn,
            addresses=addresses,
            network=network,
        )
