from __future__ import annotations

import typing
from typing_extensions import TypedDict

from .. import db_spec


class ActiveSchemas(TypedDict, total=False):
    block_gas_stats: bool
    block_timestamps: bool
    blocks: bool
    contract_abis: bool
    contract_creation_blocks: bool
    erc20_metadata: bool
    erc20_state: bool
    # events: bool


def get_active_schemas() -> typing.Mapping[db_spec.DBDatatype, bool]:
    """return specification of which subset of incoming data to store in db"""
    return {
        'block_gas_stats': False,
        'block_timestamps': True,
        'blocks': False,
        'contract_abis': True,
        'contract_creation_blocks': True,
        'erc20_metadata': True,
        'erc20_state': False,
        # 'events': False,
    }


def get_active_timestamp_schema() -> db_spec.DBDatatype | None:
    active_schemas = get_active_schemas()
    if active_schemas['block_timestamps']:
        return 'block_timestamps'
    elif active_schemas['blocks']:
        return 'blocks'
    else:
        return None
