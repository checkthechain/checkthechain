from __future__ import annotations

import typing
import re

from ctc.protocols import fourbyte_utils


async def async_decompile_function_abis(
    bytecode: str,
) -> typing.Mapping[str, str]:
    function_selectors = re.findall('8063([a-f0-9]{8})146', bytecode)

    abi = {}
    for selector in function_selectors:
        abi[selector] = await fourbyte_utils.async_query_function_signature(
            '0x' + selector
        )

    return abi

