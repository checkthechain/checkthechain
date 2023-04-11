from __future__ import annotations

import typing

from ctc import spec
from . import erc721_events
from . import erc721_spec
from . import erc721_state

if typing.TYPE_CHECKING:
    from typing_extensions import Literal


async def async_get_erc721_owners(
    token: spec.Address,
    *,
    method: Literal['transfers', 'calls'] | None = None,
    token_ids: typing.Sequence[int] | None = None,
    context: spec.Context = None,
) -> typing.Mapping[int, spec.Address]:
    """return owners of erc721 token

    can multiple methods:
    - transfers: compute owners based on erc721 transfers
    - calls: use eth_call's on enumerated list of all token_id's
    """

    if method is None:
        if token_ids is not None:
            method = 'calls'
        else:
            method = 'transfers'

    if method == 'transfers':
        transfers = await erc721_events.async_get_erc721_transfers(
            token, context=context
        )
        return _get_erc721_owners_from_transfers(transfers, token_ids=token_ids)

    elif method == 'calls':
        return await _async_get_erc721_owners_from_calls(
            token,
            token_ids=token_ids,
            context=context,
        )

    else:
        raise Exception('unknown ownership method')


def _get_erc721_owners_from_transfers(
    transfers: spec.DataFrame,
    *,
    token_ids: typing.Sequence[int] | None = None,
) -> typing.Mapping[int, spec.Address]:

    owner_transfers = (
        transfers[['arg__tokenId', 'arg__to']].groupby('arg__tokenId').last()
    )
    owner_dict = typing.cast(
        typing.Mapping[int, str],
        dict(owner_transfers.rows()),  # type: ignore
    )

    if token_ids is not None:
        filtered_owner_dict = {}
        for token_id in token_ids:
            if token_id not in owner_dict:
                raise Exception('could not find token_id in transfers')
            filtered_owner_dict[token_id] = owner_dict[token_id]
        owner_dict = filtered_owner_dict

    return owner_dict


async def _async_get_erc721_owners_from_calls(
    token: spec.Address,
    token_ids: typing.Sequence[int] | None = None,
    *,
    context: spec.Context = None,
) -> typing.Mapping[int, spec.Address]:
    from ctc import rpc

    if token_ids is None:
        try:
            total_supply = await erc721_state.async_get_erc721_total_supply(
                token,
                context=context,
            )
            token_ids = list(range(total_supply))
        except spec.RpcException:
            raise Exception(
                'this erc721 does not implement totalSupply(), to get owners from calls, need to provide token_ids directly'
            )

    results = await rpc.async_batch_eth_call(
        to_address=token,
        function_abi=erc721_spec.erc721_function_abis['ownerOf'],
        function_parameter_list=[[token_id] for token_id in token_ids],
        context=context,
    )

    return dict(zip(token_ids, results))

