from __future__ import annotations

import typing

from ctc import spec


def combine_contract_abis(
    contract_abis: typing.Sequence[spec.ContractABI],
) -> spec.ContractABI:
    """combine multiple contract ABI's into single contract ABI"""

    # insert using name to avoid name collisions
    combined = {}
    unnamed = None
    for contract_abi in contract_abis:
        for item in contract_abi:
            if item.get('name') is None:
                unnamed = item
            else:
                combined[item['name']] = item

    new_abi = list(combined.values())
    if unnamed is not None:
        new_abi.append(unnamed)

    return new_abi
