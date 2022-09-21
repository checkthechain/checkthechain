from __future__ import annotations

import typing


def extract_bytecode_function_selectors(bytecode: str) -> typing.Sequence[str]:
    """extract solidity-style function selectors from contract bytecode"""
    import re

    # solidity style signatures
    results = re.findall('8063([a-f0-9]{8})146', bytecode)

    # vyper style signatures
    if len(results) == 0:
        results = re.findall('5[b,2]63([0-9a-f]{8})600051141561', bytecode)

    return ['0x' + result for result in results]


async def async_decompile_function_abis(
    bytecode: str,
    sort: str | None = None,
) -> typing.Sequence[typing.Mapping[str, typing.Any]]:
    """decompile solidity-style function ABI's from contract bytecode"""

    from ctc.protocols import fourbyte_utils

    function_selectors = extract_bytecode_function_selectors(bytecode)

    coroutines = [
        fourbyte_utils.async_query_function_signatures(selector)
        for selector in function_selectors
    ]

    import asyncio

    abi_lists = await asyncio.gather(*coroutines)
    abis: list[fourbyte_utils.Entry] = [
        abi for abi_list in abi_lists for abi in abi_list
    ]

    if sort is not None:
        abis = sorted(abis, key=lambda item: item[sort])  # type: ignore

    return abis
