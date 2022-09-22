from __future__ import annotations

import typing

from ctc import spec

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

    class _FeedAggregatorUpdate(TypedDict):
        feed: spec.Address
        aggregator: spec.Address
        block_number: int


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
        'chainlink_aggregator_updates': {
            'columns': [
                {'name': 'feed', 'type': 'Text', 'primary': True},
                {'name': 'aggregator', 'type': 'Text', 'primary': True},
                {'name': 'block_number', 'type': 'Integer', 'primary': True},
            ],
        },
    },
}
