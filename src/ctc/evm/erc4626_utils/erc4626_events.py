from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime

from ctc import spec
from .. import event_utils
from . import erc4626_normalize
from . import erc4626_spec


async def async_get_erc4626_deposits(
    token: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    verbose: bool = False,
    normalize: bool = True,
    convert_from_str: bool = True,
    provider: spec.ProviderReference = None,
    **event_kwargs: typing.Any,
) -> spec.DataFrame:
    """get Deposit events for ERC-4626 vault"""

    event_abi = erc4626_spec.erc4626_event_abis['Deposit']

    deposits = await event_utils.async_get_events(
        contract_address=token,
        event_abi=event_abi,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
        verbose=verbose,
        provider=provider,
        **event_kwargs,
    )

    if convert_from_str:
        deposits['arg__assets'] = deposits['arg__assets'].map(int)
        deposits['arg__shares'] = deposits['arg__shares'].map(int)

    if normalize and len(deposits) > 0:
        if not convert_from_str:
            raise Exception('must convert from str with convert_from_str=True')
        blocks = deposits.index.get_level_values('block_number')
        deposits[
            'arg__assets'
        ] = await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=deposits['arg__assets'].values,  # type: ignore
            block=blocks[-1],  # type: ignore
            provider=provider,
        )
        deposits[
            'arg__shares'
        ] = await erc4626_normalize.async_normalize_erc4626_shares(
            token=token,
            shares=deposits['arg__shares'].values,  # type: ignore
            block=blocks[-1],  # type: ignore
            provider=provider,
        )

    return deposits


async def async_get_erc4626_withdraws(
    token: spec.Address,
    *,
    start_block: typing.Optional[spec.BlockNumberReference] = None,
    end_block: typing.Optional[spec.BlockNumberReference] = None,
    start_time: tooltime.Timestamp | None = None,
    end_time: tooltime.Timestamp | None = None,
    include_timestamps: bool = False,
    verbose: bool = False,
    provider: spec.ProviderReference = None,
    normalize: bool = True,
    convert_from_str: bool = True,
    **event_kwargs: typing.Any,
) -> spec.DataFrame:
    """get Withdraw events for ERC-4626 vault"""

    event_abi = erc4626_spec.erc4626_event_abis['Withdraw']

    withdraws = await event_utils.async_get_events(
        contract_address=token,
        event_abi=event_abi,
        start_block=start_block,
        end_block=end_block,
        start_time=start_time,
        end_time=end_time,
        include_timestamps=include_timestamps,
        verbose=verbose,
        provider=provider,
        **event_kwargs,
    )

    if convert_from_str:
        withdraws['arg__assets'] = withdraws['arg__assets'].map(int)
        withdraws['arg__shares'] = withdraws['arg__shares'].map(int)

    if normalize and len(withdraws) > 0:
        if not convert_from_str:
            raise Exception('must convert from str with convert_from_str=True')
        blocks = withdraws.index.get_level_values('block_number')
        withdraws[
            'arg__assets'
        ] = await erc4626_normalize.async_normalize_erc4626_assets(
            token=token,
            assets=withdraws['arg__assets'].values,  # type: ignore
            block=blocks[-1],  # type: ignore
            provider=provider,
        )
        withdraws[
            'arg__shares'
        ] = await erc4626_normalize.async_normalize_erc4626_shares(
            token=token,
            shares=withdraws['arg__shares'].values,  # type: ignore
            block=blocks[-1],  # type: ignore
            provider=provider,
        )

    return withdraws
