from __future__ import annotations

from ctc import spec
from .. import connect_utils
from .. import db_crud
from .. import db_management
from . import intake_utils


async def async_intake_contract_creation_block(
    contract_address: spec.Address,
    block: int,
    network: spec.NetworkReference,
) -> None:
    if 'contract_creation_blocks' not in db_management.get_active_schemas():
        return
    confirmed = await intake_utils.async_is_block_fully_confirmed(
        block=block, network=network
    )
    if not confirmed:
        return

    engine = connect_utils.create_engine(datatype='contract_creation_blocks')
    if engine is not None:
        with engine.begin() as conn:
            await db_crud.async_store_contract_creation_block(
                conn=conn,
                block_number=block,
                address=contract_address,
                network=network,
            )