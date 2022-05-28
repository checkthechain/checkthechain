from __future__ import annotations

from ctc import spec
from ... import connect_utils
from ... import query_utils
from . import contract_abis_statements


async def async_query_contract_abi(
    address: spec.Address,
    network: spec.NetworkReference,
) -> spec.ContractABI | None:
    engine = connect_utils.create_engine(
        schema_name='contract_abis',
        network=network,
    )
    if engine is None:
        return None
    with engine.connect() as conn:
        return await contract_abis_statements.async_select_contract_abi(
            conn=conn,
            address=address,
            network=network,
        )


async_query_contract_abis = query_utils.with_connection(
    contract_abis_statements.async_select_contract_abis,
    'contract_abis',
)
