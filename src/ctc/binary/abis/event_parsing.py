from __future__ import annotations

from ctc import binary
from ctc import spec
from . import function_parsing


def get_event_hash(event_abi: spec.EventABI) -> str:
    """compute event hash from event's abi"""
    signature = get_event_signature(event_abi=event_abi)
    return binary.keccak_text(signature)


def get_event_signature(event_abi: spec.EventABI) -> str:
    arg_types = [var['type'] for var in event_abi['inputs']]
    arg_types = [
        function_parsing.get_function_selector_type(item) for item in arg_types
    ]
    inputs = ','.join(arg_types)
    return event_abi['name'] + '(' + inputs + ')'


def get_event_unindexed_types(
    event_abi: spec.EventABI,
) -> list[spec.ABIDatumType]:
    """get list of data types in signature of event"""
    return [var['type'] for var in event_abi['inputs'] if not var['indexed']]


def get_event_unindexed_names(event_abi: spec.EventABI) -> list[str]:
    """get list of data names in signature of event"""
    return [var['name'] for var in event_abi['inputs'] if not var['indexed']]


def get_event_indexed_names(event_abi: spec.EventABI) -> list[str]:
    """get list of indexed names in signature of event"""
    return [var['name'] for var in event_abi['inputs'] if var['indexed']]


def get_event_indexed_types(
    event_abi: spec.EventABI,
) -> list[spec.ABIDatumType]:
    """get list of indexed types in signature of event"""
    return [var['type'] for var in event_abi['inputs'] if var['indexed']]

