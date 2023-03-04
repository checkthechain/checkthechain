from __future__ import annotations

import toolsql

from ctc import config
from ctc import spec
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

    db_config = config.get_context_db_config(
        schema_name='contract_creation_blocks',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        confirmed = await intake_utils.async_is_block_fully_confirmed(
            block=block, context=context, conn=conn
        )
        if not confirmed:
            return
        await contract_creation_blocks_statements.async_upsert_contract_creation_block(
            conn=conn,
            block_number=block,
            address=contract_address,
            context=context,
        )

