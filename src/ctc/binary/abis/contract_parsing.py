from __future__ import annotations

import typing

from ctc import spec

from .. import formats
from . import function_parsing
from . import event_parsing


def get_function_abi(
    contract_abi: spec.ContractABI,
    function_name: typing.Optional[str] = None,
    n_parameters: typing.Optional[int] = None,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
    function_selector: typing.Optional[spec.FunctionSelector] = None,
) -> spec.FunctionABI:

    if function_selector is not None:
        function_selector = formats.convert(function_selector, 'prefix_hex')

    candidates = []
    for item in contract_abi:
        if item.get('type') != 'function':
            continue
        else:
            function_abi = typing.cast(spec.FunctionABI, item)

        if (
            function_name is not None
            and function_abi.get('name') != function_name
        ):
            continue
        if (
            n_parameters is not None
            and len(function_abi['inputs']) != n_parameters
        ):
            continue
        if parameter_types is not None:
            types = function_parsing.get_function_parameter_types(function_abi)
            if parameter_types != tuple(types):
                continue
        if function_selector is not None:
            item_selector = function_parsing.get_function_selector(function_abi)
            item_selector = formats.convert(item_selector, 'prefix_hex')
            if item_selector != function_selector:
                continue
        candidates.append(function_abi)

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise LookupError('could not find function abi')
    elif len(candidates) > 0:
        import json

        as_json = [json.dumps(candidate) for candidate in candidates]
        if all(as_json[0] == entry for entry in as_json[1:]):
            return candidates[0]

        raise LookupError('too many candidates found for function abi')
    else:
        raise Exception('internal error')


def get_event_abi(
    *,
    contract_abi: spec.ContractABI,
    event_name: typing.Optional[str] = None,
    event_hash: typing.Optional[str] = None,
    event_abi: typing.Optional[spec.EventABI] = None,
) -> spec.EventABI:
    """get event abi from contract abi"""

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
            item_hash = event_parsing.get_event_hash(event_abi=item)
            if item_hash != event_hash:
                continue

        candidates.append(item)

    if len(candidates) == 0:
        raise Exception('could not find event abi')
    elif len(candidates) == 1:
        return candidates[0]
    else:
        raise Exception('found too many candidates for event abi')

