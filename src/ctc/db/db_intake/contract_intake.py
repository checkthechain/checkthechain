from __future__ import annotations

from ctc import spec
from .. import db_connect
from .. import db_statements
from .. import db_management
from . import intake_utils


async def async_intake_contract_creation_block(
    contract_address: spec.Address,
    block: int,
    network: spec.NetworkReference,
) -> None:

    if not db_management.get_active_schemas().get('contract_creation_blocks'):
        return
    confirmed = await intake_utils.async_is_block_fully_confirmed(
        block=block, network=network
    )
    if not confirmed:
        return

    engine = db_connect.create_engine(
        datatype='contract_creation_blocks',
        network=network,
    )
    if engine is not None:
        with engine.begin() as conn:
            await db_statements.async_upsert_contract_creation_block(
                conn=conn,
                block_number=block,
                address=contract_address,
                network=network,
            )


async def async_intake_contract_abi(
    contract_address: spec.Address,
    network: spec.NetworkReference,
    abi: spec.ContractABI,
    includes_proxy: bool,
) -> None:

    if not db_management.get_active_schemas().get('contract_abis'):
        return
    engine = db_connect.create_engine(
        datatype='contract_abis',
        network=network,
    )
    if engine is not None:
        with engine.begin() as conn:
            await db_statements.async_upsert_contract_abi(
                address=contract_address,
                abi=abi,
                includes_proxy=includes_proxy,
                conn=conn,
                network=network,
            )
