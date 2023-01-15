from __future__ import annotations

import typing
from ctc import spec
from . import consensus_requests


#
# # epochs
#


async def async_get_consensus_finalized_epoch(
    *,
    state_id: str = 'head',
    context: spec.Context = None,
) -> int:
    result: spec.ConsensusFinalityCheckpoints = (
        await consensus_requests.async_beacon_request(
            'beacon_finality_checkpoints',
            params=dict(state_id=state_id),
            context=context,
        )
    )
    return int(result['finalized']['epoch'])


async def async_get_consensus_justified_epoch(
    *,
    state_id: str = 'head',
    context: spec.Context = None,
) -> int:
    result: spec.ConsensusFinalityCheckpoints = (
        await consensus_requests.async_beacon_request(
            'beacon_finality_checkpoints',
            params=dict(state_id=state_id),
            context=context,
        )
    )
    return int(result['current_justified']['epoch'])


#
# # slots
#


async def async_get_consensus_current_slot(
    *,
    context: spec.Context = None,
) -> int:
    result: typing.Any = await consensus_requests.async_beacon_request(
        'beacon_syncing', context=context
    )
    return int(result['head_slot'])


#
# # validators
#


async def async_get_consensus_validators(
    *,
    state_id: str = 'head',
    context: spec.Context = None,
) -> typing.Sequence[spec.ConsensusValidator]:
    result: typing.Sequence[
        spec.ConsensusValidator
    ] = await consensus_requests.async_beacon_request(
        'beacon_validators',
        params=dict(state_id=state_id),
        context=context,
    )
    return result


async def async_get_consensus_validator(
    *,
    state_id: str = 'head',
    context: spec.Context = None,
) -> spec.ConsensusValidator:

    result: spec.ConsensusValidator = (
        await consensus_requests.async_beacon_request(
            'beacon_validator',
            params=dict(state_id=state_id),
            context=context,
        )
    )
    return result


async def async_get_consensus_validator_count(
    *,
    state_id: str = 'head',
    context: spec.Context = None,
) -> int:
    validators = await async_get_consensus_validators(
        state_id=state_id,
        context=context,
    )
    return len(validators)


#
# # peers
#


async def async_get_consensus_peers(
    *,
    context: spec.Context = None,
) -> typing.Sequence[spec.ConsensusPeer]:
    result: typing.Sequence[
        spec.ConsensusPeer
    ] = await consensus_requests.async_beacon_request(
        'node_peers',
        context=context,
    )
    return result


async def async_get_consensus_peer(
    peer_id: str,
    *,
    context: spec.Context = None,
) -> spec.ConsensusPeer:
    result: spec.ConsensusPeer = await consensus_requests.async_beacon_request(
        'node_peer',
        params=dict(peer_id=peer_id),
        context=context,
    )
    return result


async def async_get_consensus_peer_count(
    *,
    context: spec.Context = None,
) -> typing.Mapping[str, int]:
    result: typing.Mapping[
        str, str
    ] = await consensus_requests.async_beacon_request(
        'node_peer_count',
        context=context,
    )
    return {k: int(v) for k, v in result.items()}


#
# # setup
#


async def async_get_consensus_deposit_contract(
    *,
    context: spec.Context = None,
) -> spec.Address:
    result: spec.Address = await consensus_requests.async_beacon_request(
        'config_deposit_contract',
        context=context,
    )
    return result


#
# # node
#


async def async_get_consensus_client_version(
    *,
    context: spec.Context = None,
) -> str:
    result: str = await consensus_requests.async_beacon_request(
        'node_version',
        context=context,
    )
    return result


async def async_get_consensus_client_id(
    *,
    context: spec.Context = None,
) -> str:
    result: str = await consensus_requests.async_beacon_request(
        'node_identity',
        context=context,
    )
    return result

