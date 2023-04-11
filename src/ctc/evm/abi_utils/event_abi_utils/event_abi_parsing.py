from __future__ import annotations

from ctc import spec
from ... import binary_utils
from .. import function_abi_utils


def get_event_hash(event_data: spec.EventABI | str) -> str:
    """compute event hash from event signature or event abi"""
    if isinstance(event_data, str):
        signature = event_data
    else:
        signature = get_event_signature(event_abi=event_data)
    return binary_utils.keccak_text(signature)


def get_event_signature(event_abi: spec.EventABI) -> str:
    """get event signature from event ABI"""
    import eth_utils_lite  # type: ignore

    base_arg_types = [var['type'] for var in event_abi['inputs']]
    arg_types = []
    for i, item in enumerate(base_arg_types):
        if item.startswith('tuple'):
            arg_type = eth_utils_lite.abi.collapse_if_tuple(
                event_abi['inputs'][i]
            )
        else:
            arg_type = function_abi_utils.get_function_selector_type(item)
        arg_types.append(arg_type)
    inputs = ','.join(arg_types)
    return event_abi['name'] + '(' + inputs + ')'


def get_event_unindexed_types(
    event_abi: spec.EventABI,
) -> list[spec.ABIDatumType]:
    """get list of data types in signature of event"""

    import eth_utils_lite

    return [
        eth_utils_lite.abi.collapse_if_tuple(var)
        for var in event_abi['inputs']
        if not var['indexed']
    ]


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


def get_event_schema(event_abi: spec.EventABI) -> spec.EventSchema:
    """return schema of types and names of event"""
    indexed_names = get_event_indexed_names(event_abi)
    indexed_types = get_event_indexed_types(event_abi)
    unindexed_names = get_event_unindexed_names(event_abi)
    unindexed_types = get_event_unindexed_types(event_abi)
    return {
        'indexed_names': indexed_names,
        'indexed_types': indexed_types,
        'unindexed_names': unindexed_names,
        'unindexed_types': unindexed_types,
        'names': indexed_names + unindexed_names,
        'types': indexed_types + unindexed_types,
    }

