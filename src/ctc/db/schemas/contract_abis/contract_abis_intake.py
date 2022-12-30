from __future__ import annotations

from ctc import spec
from ... import connect_utils
from ... import management

from . import contract_abis_statements


async def async_intake_contract_abi(
    abi: spec.ContractABI,
    contract_address: spec.Address,
    *,
    context: spec.Context = None,
    includes_proxy: bool,
) -> None:
    """block age not checked because abis are not usually acquired from reorg-ably young blocks"""

    # validate input format
    if not isinstance(abi, list):
        raise Exception('bad format for contract abi')
    if any(not isinstance(item, dict) for item in abi):
        raise Exception('bad format for contract abi')

    if not management.get_active_schemas().get('contract_abis'):
        return

    engine = connect_utils.create_engine(
        schema_name='contract_abis',
        context=context,
    )
    if engine is not None:
        with engine.begin() as conn:
            await contract_abis_statements.async_upsert_contract_abi(
                address=contract_address,
                abi=abi,
                includes_proxy=includes_proxy,
                conn=conn,
                context=context,
            )
