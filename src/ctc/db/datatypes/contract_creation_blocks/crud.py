from __future__ import annotations

import toolsql

from ctc import spec


def set_contract_creation_block(
    conn: toolsql.SAConnection,
    contract_address: spec.Address,
    block: int,
    network: spec.NetworkReference | None = None,
) -> None:
    pass


def get_contract_creation_block(
    conn: toolsql.SAConnection,
    contract_address: spec.Address,
    network: spec.NetworkReference | None = None,
):
    pass

