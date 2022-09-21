from __future__ import annotations

import typing

from ctc import spec
from ... import binary_utils
from . import function_abi_queries


def function_signature_to_abi(function_signature: str) -> spec.FunctionABI:
    """return a partial ABI of function from just a signature

    will be missing input parameter names and information about outputs
    """
    function_name, tail = function_signature.split('(')
    parameters, _ = tail.split(')')
    parameter_types = parameters.split(',')

    return {
        'type': 'function',
        'name': function_name,
        'inputs': [
            {'type': parameter_type} for parameter_type in parameter_types
        ],
        'outputs': [],
    }


async def async_parse_function_str_abi(
    function: str,
    contract_address: spec.Address | None = None,
) -> spec.FunctionABI:
    """parse a function str into a function ABI

    function str can be a function name, 4byte selector, or ABI

    used for cli commands
    """

    if is_function_selector(function):
        # function given as a function selector
        function_name = None
        function_selector = function
        function_abi = None
    elif is_function_signature(function):
        return function_signature_to_abi(function)
    else:
        try:
            # function given as json / python dict str
            import ast

            function_name = None
            function_selector = None
            function_abi = ast.literal_eval(function)
        except Exception:
            # function given as a function name
            function_name = function
            function_selector = None
            function_abi = None

    if function_abi is None:
        function_abi = await function_abi_queries.async_get_function_abi(
            contract_address=contract_address,
            function_name=function_name,
            function_selector=function_selector,
        )

    return function_abi


def get_function_parameter_types(
    function_abi: spec.FunctionABI | None = None,
    function_signature: typing.Optional[str] = None,
) -> list[spec.ABIDatumType]:
    """return list of function parameter types"""

    if function_abi is not None:

        output = []
        for item in function_abi.get('inputs', []):
            import eth_utils_lite  # type: ignore

            cast_item = typing.cast(typing.Dict[str, typing.Any], item)
            collapsed = eth_utils_lite.abi.collapse_if_tuple(cast_item)
            output.append(collapsed)

        return output

    elif function_signature is not None:
        parameter_str = function_signature.split('(')[1]
        parameter_str = parameter_str[:-1]
        return parameter_str.split(',')

    else:
        raise Exception('must specify function_abi or function_signature')


@typing.overload
def get_function_parameter_names(
    function_abi: spec.FunctionABI,
    require_names: typing.Literal[True],
) -> list[str]:
    ...


@typing.overload
def get_function_parameter_names(
    function_abi: spec.FunctionABI,
    require_names: typing.Literal[False] = False,
) -> list[typing.Optional[str]]:
    ...


def get_function_parameter_names(
    function_abi: spec.FunctionABI,
    require_names: bool = False,
) -> typing.Union[list[str], list[typing.Optional[str]]]:
    """return list of function parameter names"""

    names = [item.get('name') for item in function_abi.get('inputs', [])]

    if require_names:
        if any(name is None for name in names):
            raise Exception('function abi does not specify names')
        else:
            return typing.cast(typing.List[str], names)
    else:
        return names


def get_function_signature(
    function_abi: spec.FunctionABI | None = None,
    *,
    parameter_types: typing.Optional[list[str]] = None,
    function_name: typing.Optional[str] = None,
    include_names: bool = False,
) -> str:
    """return function signature"""

    # get parameter types
    if parameter_types is None:
        parameter_types = get_function_parameter_types(function_abi)
    parameter_types = [
        get_function_selector_type(item) for item in parameter_types
    ]

    # create entires with or without names
    if include_names:
        if function_abi is None:
            raise Exception('must specify function_abi')
        parameter_names = get_function_parameter_names(
            function_abi, require_names=True
        )
        entries = [
            type + ' ' + name
            for type, name in zip(parameter_types, parameter_names)
        ]
        entries_str = ', '.join(entries)
    else:
        entries = parameter_types
        entries_str = ','.join(entries)

    if function_name is None:
        if function_abi is None:
            raise Exception('must specify function_abi')
        function_name = function_abi['name']

    return function_name + '(' + entries_str + ')'


def get_function_selector_type(
    datatype: spec.ABIDatumType,
) -> spec.ABIDatumType:
    """get the data name used for function selector"""
    if datatype == 'uint':
        return 'uint256'
    elif datatype == 'int':
        return 'int256'
    elif datatype == 'ufixed':
        return 'ufixed128x18'
    elif datatype == 'fixed':
        return 'fixed128x18'
    else:
        return datatype


def get_function_selector(
    function_abi: typing.Optional[spec.FunctionABI] = None,
    function_signature: typing.Optional[spec.FunctionSignature] = None,
) -> str:
    """get function 4 byte selector"""

    if function_signature is None:
        if function_abi is None:
            raise Exception('must specify function_abi or function_signature')
        function_signature = get_function_signature(function_abi)

    full_hash = binary_utils.keccak(
        function_signature.encode(), output_format='raw_hex'
    )
    return full_hash[:8]


def is_function_selector(selector: typing.Any) -> bool:
    """return whether input is a function selector"""
    return isinstance(selector, str) and (
        (spec.is_prefix_hex_data(selector) and len(selector) == 10)
        or (spec.is_raw_hex_data(selector) and len(selector) == 8)
    )


def is_function_signature(signature: typing.Any) -> bool:
    """return whether a str is a function signature

    this is NOT a comprehensive test, only an approximation using regexes
    """
    if isinstance(signature, str):
        import re

        return re.fullmatch('[a-zA-Z_].*\([a-z,\[\]]*\)', signature) is not None
    return False


def get_function_output_types(
    function_abi: spec.FunctionABI,
) -> list[spec.ABIDatumType]:
    """return list of function output types"""

    import eth_utils_lite

    output_types = []
    for output in function_abi['outputs']:
        cast_output = typing.cast(typing.Dict[str, typing.Any], output)
        output_type = eth_utils_lite.abi.collapse_if_tuple(cast_output)
        output_types.append(output_type)
    return output_types


def get_function_output_names(
    function_abi: spec.FunctionABI,
    human_readable: bool = False,
) -> list[typing.Optional[str]]:
    """return list of function output names"""

    output_names = [output.get('name') for output in function_abi['outputs']]

    # human readable uses function name or output_# if no names provided
    if human_readable:
        if len(output_names) == 1:
            if output_names[0] == '':
                output_names[0] = function_abi.get('name')
        else:
            for on, output_name in list(enumerate(output_names)):
                if output_name == '':
                    output_names[on] == 'output_' + str(on)

    return output_names


def is_function_read_only(function_abi: spec.FunctionABI) -> bool:
    """return whether function is read-only"""
    return bool(function_abi.get('constant')) or (
        function_abi.get('stateMutability')
        in (
            'view',
            'pure',
        )
    )
