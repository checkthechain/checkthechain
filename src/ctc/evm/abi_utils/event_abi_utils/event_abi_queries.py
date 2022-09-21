from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from .. import contract_abi_utils
from . import event_abi_parsing


def get_event_abi(
    *,
    contract_abi: spec.ContractABI,
    event_name: typing.Optional[str] = None,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
) -> spec.EventABI:
    """get event ABI from contract ABI"""

    if event_abi is not None:
        return event_abi

    if event_name is None and event_hash is None:
        raise Exception('specify event_name or event_hash')

    candidates = []
    for item in contract_abi:
        if item['type'] != 'event':
            continue
        if event_name is not None and item.get('name') != event_name:
            continue
        if event_hash is not None:
            item_hash = event_abi_parsing.get_event_hash(event_abi=item)
            if item_hash != event_hash:
                continue

        candidates.append(item)

    if len(candidates) == 0:
        raise LookupError('could not find event abi')
    elif len(candidates) == 1:
        return candidates[0]
    else:
        raise Exception('found too many candidates for event abi')


async def async_get_event_abi(
    *,
    contract_abi: typing.Optional[spec.ContractABI] = None,
    contract_address: typing.Optional[spec.Address] = None,
    event_name: typing.Optional[str] = None,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
    network: typing.Optional[spec.NetworkReference] = None,
) -> spec.EventABI:
    """get event ABI from local database or block explorer"""

    # get contract abi
    if contract_abi is None:
        if contract_address is None:
            raise Exception('must specify contract_abi or contract_address')
        contract_abi = await contract_abi_utils.async_get_contract_abi(
            contract_address=contract_address,
            network=network,
        )

    try:
        return evm.get_event_abi(
            contract_abi=contract_abi,
            event_name=event_name,
            event_hash=event_hash,
            event_abi=event_abi,
        )

    except LookupError as e:

        # query contract_abi again if contract abi might have changed since db
        if contract_address is not None:
            contract_abi = await contract_abi_utils.async_get_contract_abi(
                contract_address=contract_address,
                network=network,
                db_query=False,
            )

            return evm.get_event_abi(
                contract_abi=contract_abi,
                event_name=event_name,
                event_hash=event_hash,
                event_abi=event_abi,
            )

        else:
            raise e


def get_event_abis(
    contract_abi: spec.ContractABI,
) -> typing.Sequence[spec.EventABI]:
    """get event ABI's from contract ABI"""
    return [item for item in contract_abi if item['type'] == 'event']
