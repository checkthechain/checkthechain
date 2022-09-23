from __future__ import annotations

import typing

from ctc import spec
from . import contract_abi_summary


def get_contract_abi_diff(
    first_contract_abi: spec.ContractABI,
    second_contract_abi: spec.ContractABI,
) -> typing.Mapping[str, spec.ContractABI]:
    """return difference between two contract ABI's"""

    first_by_selectors = contract_abi_summary.get_contract_abi_by_selectors(
        first_contract_abi
    )
    second_by_selectors = contract_abi_summary.get_contract_abi_by_selectors(
        second_contract_abi
    )

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
    """print difference between contract ABI's"""

    if first_name is None:
        first_name = 'First Contract'
    if second_name is None:
        second_name = 'Second Contract'

    diff = get_contract_abi_diff(first_contract_abi, second_contract_abi)

    if functions_only or not events_only:

        contract_abi_summary.print_contract_abi_functions(
            diff['mutual'],
            title='Mutual Functions',
        )

        print()
        print()
        contract_abi_summary.print_contract_abi_functions(
            diff['first_only'],
            title=first_name + ' Functions',
        )

        print()
        print()
        contract_abi_summary.print_contract_abi_functions(
            diff['second_only'],
            title=second_name + ' Functions',
        )

    if events_only or not functions_only:

        if functions_only or not events_only:
            print()
            print()

        contract_abi_summary.print_contract_abi_events(
            diff['mutual'],
            title='Mutual Events',
        )

        print()
        print()
        contract_abi_summary.print_contract_abi_events(
            diff['first_only'],
            title=first_name + ' Events',
        )

        print()
        print()
        contract_abi_summary.print_contract_abi_events(
            diff['second_only'],
            title=second_name + ' Events',
        )
