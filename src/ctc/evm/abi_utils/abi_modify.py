from __future__ import annotations

import typing

from ctc import spec


def combine_contract_abis(
    contract_abis: typing.Sequence[spec.ContractABI],
) -> spec.ContractABI:

    # insert using name to avoid name collisions
    combined = {}
    for contract_abi in contract_abis:
        for item in contract_abi:
            combined[item['name']] = item

    return list(combined.values())
