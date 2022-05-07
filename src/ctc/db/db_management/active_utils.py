from __future__ import annotations

import typing
from typing_extensions import TypedDict


class ActiveSchemas(TypedDict, total=False):
    blocks: bool
    block_timestamps: bool
    block_gas_stats: bool
    contract_creation_blocks: bool
    erc20_metadata: bool
    erc20_balances: bool
    erc20_total_supplies: bool
    events: bool


def get_active_schemas() -> typing.Mapping[str, bool]:
    """return specification of which subset of incoming data to store in db"""
    return {
        'blocks': False,
        'block_timestamps': True,
        'block_gas_stats': False,
        'contract_creation_blocks': True,
        'erc20_metadata': True,
        'erc20_balances': False,
        'erc20_total_supplies': False,
        'events': False,
    }


def get_active_timestamp_schema() -> str | None:
    active_schemas = get_active_schemas()
    if active_schemas['block_timestamps']:
        return 'block_timestamps'
    elif active_schemas['blocks']:
        return 'blocks'
    else:
        return None
