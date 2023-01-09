from __future__ import annotations

import toolsql

from ctc import spec
from .. import connect_utils
from .. import schema_utils


def get_table_row_count(
    table: str,
    *,
    schema_name: spec.SchemaName | None = None,
    context: spec.Context = None,
) -> int | None:
    table_name = schema_utils.get_table_name(table, context=context)
    if schema_name is None:
        schema_name = schema_utils.get_schema_of_raw_table(table)
    engine = connect_utils.create_engine(schema_name, context=context)
    if engine is None:
        return None
    with engine.connect() as conn:
        row_count = toolsql.get_table_row_count(table_name, conn=conn)
    return row_count

