from __future__ import annotations

from ctc import spec
from ... import connect_utils
from ... import intake_utils
from ... import management

from . import contract_creation_blocks_statements


async def async_intake_contract_creation_block(
    contract_address: spec.Address,
    block: int,
    *,
    context: spec.Context = None,
) -> None:

    if not management.get_active_schemas().get('contract_creation_blocks'):
        return
    confirmed = await intake_utils.async_is_block_fully_confirmed(
        block=block, context=context
    )
    if not confirmed:
        return

    engine = connect_utils.create_engine(
        schema_name='contract_creation_blocks',
        context=context,
    )
    if engine is not None:
        with engine.begin() as conn:
            await contract_creation_blocks_statements.async_upsert_contract_creation_block(
                conn=conn,
                block_number=block,
                address=contract_address,
                context=context,
            )
