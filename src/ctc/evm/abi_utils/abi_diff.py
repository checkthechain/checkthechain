from __future__ import annotations

import typing

from ctc import binary
from ctc import spec
from . import abi_summary


def map_contract_abi_by_selectors(
    contract_abi: spec.ContractABI,
) -> typing.Mapping[str, spec.ContractABIEntry]:
    by_selectors: typing.MutableMapping[str, spec.ContractABIEntry] = {}
    for item in contract_abi:
        if item['type'] == 'function':
            function_selector = binary.get_function_selector(item)
            by_selectors[function_selector] = item
        elif item['type'] == 'event':
            event_hash = binary.get_event_hash(item)
            by_selectors[event_hash] = item
        elif item['type'] in ['error', 'constructor']:
            pass
        else:
            raise Exception('unknown item type in contract abi')
    return by_selectors


def get_contract_abi_diff(
    first_contract_abi: spec.ContractABI,
    second_contract_abi: spec.ContractABI,
) -> typing.Mapping[str, spec.ContractABI]:

    first_by_selectors = map_contract_abi_by_selectors(first_contract_abi)
    second_by_selectors = map_contract_abi_by_selectors(second_contract_abi)

    mutual = []
    first_only = []
    second_only = []

    for key, value in first_by_selectors.items():
        if key in second_by_selectors:
            mutual.append(value)
        else:
            first_only.append(value)
    for key, value in second_by_selectors.items():
        if key not in first_by_selectors:
            second_only.append(value)

    return {
        'mutual': mutual,
        'first_only': first_only,
        'second_only': second_only,
    }


def print_contract_abi_diff(
    first_contract_abi: spec.ContractABI,
    second_contract_abi: spec.ContractABI,
    *,
    first_name: str | None = None,
    second_name: str | None = None,
    functions_only: bool = False,
    events_only: bool = False,
) -> None:

    if first_name is None:
        first_name = 'First Contract'
    if second_name is None:
        second_name = 'Second Contract'

    diff = get_contract_abi_diff(first_contract_abi, second_contract_abi)

    if functions_only or not events_only:

        abi_summary.print_contract_abi_functions_human_readable(
            diff['mutual'],
            title='Mutual Functions',
        )

        print()
        print()
        abi_summary.print_contract_abi_functions_human_readable(
            diff['first_only'],
            title=first_name + ' Functions',
        )

        print()
        print()
        abi_summary.print_contract_abi_functions_human_readable(
            diff['second_only'],
            title=second_name + ' Functions',
        )

    if events_only or not functions_only:

        if functions_only or not events_only:
            print()
            print()

        abi_summary.print_contract_abi_events_human_readable(
            diff['mutual'],
            title='Mutual Events',
        )

        print()
        print()
        abi_summary.print_contract_abi_events_human_readable(
            diff['first_only'],
            title=first_name + ' Events',
        )

        print()
        print()
        abi_summary.print_contract_abi_events_human_readable(
            diff['second_only'],
            title=second_name + ' Events',
        )
