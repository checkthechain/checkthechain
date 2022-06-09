from __future__ import annotations

from typing_extensions import TypedDict

import toolsql

from ctc import spec


class ERC20Metadata(TypedDict):
    address: spec.Address
    symbol: str
    decimals: int


erc20_metadata_schema: toolsql.DBSchema = {
    'tables': {
        'erc20_metadata': {
            'columns': [
                {
                    'name': 'address',
                    'type': 'Text',
                    'primary': True,
                },
                {
                    'name': 'symbol',
                    'type': 'Text',
                    'index': True,
                },
                {
                    'name': 'decimals',
                    'type': 'Integer',
                },
                {
                    'name': 'name',
                    'type': 'Text',
                    'index': True,
                },
            ],
        },
    },
}
