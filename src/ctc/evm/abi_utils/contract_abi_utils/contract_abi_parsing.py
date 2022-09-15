from __future__ import annotations

from ctc import evm
from ctc import spec
from .. import function_abi_utils


async def async_parse_function_str_abi(
    function: str,
    contract_address: spec.Address | None = None,
) -> spec.FunctionABI:
    """parse a function str into a function ABI

    function str can be a function name, 4byte selector, or ABI

    used for cli commands
    """

    if function_abi_utils.is_function_selector(function):
        function_name = None
        function_selector = function
        function_abi = None
    else:
        try:
            import ast

            function_name = None
            function_selector = None
            function_abi = ast.literal_eval(function)
        except Exception:
            function_name = function
            function_selector = None
            function_abi = None

    if function_abi is None:
        function_abi = await evm.async_get_function_abi(
            contract_address=contract_address,
            function_name=function_name,
            function_selector=function_selector,
        )

    return function_abi
