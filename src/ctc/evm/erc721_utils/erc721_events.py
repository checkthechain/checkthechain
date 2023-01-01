from __future__ import annotations

from ctc import spec
from .. import event_utils
from . import erc721_spec


async def async_get_erc721_transfers(
    token: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    """get transfers of erc721 token"""
    return await event_utils.async_get_events(
        contract_address=token,
        event_abi=erc721_spec.erc721_event_abis['Transfer'],
        verbose=False,
        start_block=start_block,
        end_block=end_block,
        context=context,
    )


async def async_get_erc721_approvals(
    token: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    """get approval of erc721 token"""
    return await event_utils.async_get_events(
        contract_address=token,
        event_abi=erc721_spec.erc721_event_abis['Approve'],
        verbose=False,
        start_block=start_block,
        end_block=end_block,
        context=context,
    )


async def async_get_erc721_approvals_for_all(
    token: spec.Address,
    *,
    start_block: spec.BlockNumberReference | None = None,
    end_block: spec.BlockNumberReference | None = None,
    context: spec.Context = None,
) -> spec.DataFrame:
    """get approvals for all of erc721 token"""
    return await event_utils.async_get_events(
        contract_address=token,
        event_abi=erc721_spec.erc721_event_abis['ApproveForAll'],
        verbose=False,
        start_block=start_block,
        end_block=end_block,
        context=context,
    )
