from __future__ import annotations

from typing_extensions import Literal, TypedDict

from ctc import spec


DBDatatype = Literal[
    'block_gas_stats',
    'block_timestamps',
    'blocks',
    'contract_abis',
    'contract_creation_blocks',
    'erc20_metadata',
    'erc20_state',
    # 'events',
]


class ERC20Metadata(TypedDict):
    address: spec.Address
    symbol: str
    decimals: int


def get_all_datatypes() -> tuple[DBDatatype]:
    return DBDatatype.__args__  # type: ignore
