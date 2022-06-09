from __future__ import annotations

import typing

if typing.TYPE_CHECKING:

    from typing_extensions import TypedDict

    import toolsql

    class ChainlinkFeed(TypedDict):
        address: str
        name: str
        deviation: str
        heartbeat: str
        decimals: int
        asset: str
        asset_type: str
        status: str


chainlink_schema: toolsql.DBSchema = {
    'tables': {
        'chainlink_feeds': {
            'columns': [
                {'name': 'address', 'type': 'Text', 'primary': True},
                {'name': 'name', 'type': 'Text', 'index': True},
                {'name': 'deviation', 'type': 'Text'},
                {'name': 'heartbeat', 'type': 'Text'},
                {'name': 'decimals', 'type': 'Integer'},
                {'name': 'asset', 'type': 'Text', 'index': True},
                {'name': 'asset_type', 'type': 'Text', 'index': True},
                {'name': 'status', 'type': 'Text'},
            ],
        },
    },
}
