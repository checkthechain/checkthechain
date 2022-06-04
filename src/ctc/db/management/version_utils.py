from __future__ import annotations

import typing

from .. import schemas


async def async_get_table_version(table_name) -> str:
    updates = await schemas.async_query_schema_updates(
        table_name=table_name,
    )
    most_recent = sorted(updates, key=lambda update: update['timestamp'])[-1]
    return most_recent['version']


async def async_get_tables_versions() -> typing.Mapping[str, str]:

    # load updates
    updates = await schemas.async_query_schema_updates()

    # find most recent update for each table
    table_timestamps = {}
    table_versions = {}
    for update in updates:
        table_name = update['table_name']
        if table_name not in table_timestamps:
            table_timestamps[table_name] = update['timestamp']
            table_versions[table_name] = update['version']
        else:
            if update['timestamp'] > table_timestamps[table_name]:
                table_timestamps[table_name] = update['timestamp']
                table_versions[table_name] = update['version']

    return table_versions
