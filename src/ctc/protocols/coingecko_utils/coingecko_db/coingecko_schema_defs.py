from __future__ import annotations

import typing

if typing.TYPE_CHECKING:

    from typing_extensions import TypedDict
    import toolsql

    class CoingeckoToken(TypedDict):
        id: str
        symbol: str
        name: str
        market_cap_rank: int


coingecko_schema: toolsql.DBSchema = {
    'tables': {
        'coingecko_tokens': {
            'columns': [
                {'name': 'id', 'type': 'Text', 'primary': True},
                {
                    'name': 'symbol',
                    'type': 'Text',
                    'index': True,
                },
                {'name': 'name', 'type': 'Text', 'index': True},
                {'name': 'market_cap_rank', 'type': 'Integer', 'index': True},
            ],
        },
    },
}
