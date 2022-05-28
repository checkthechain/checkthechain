from __future__ import annotations

import typing

from ... import connect_utils
from . import schema_updates_statements


async def async_query_schema_updates(
    table_name: str,
) -> None | typing.Sequence[typing.Mapping[typing.Any, typing.Any]]:
    engine = connect_utils.create_engine(
        schema_name='schema_updates',
        network=None,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await schema_updates_statements.async_select_schema_updates(
            table_name=table_name,
            conn=conn,
        )
