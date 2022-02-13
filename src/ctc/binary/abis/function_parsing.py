from __future__ import annotations

import typing

from ctc import spec

from .. import hashes


def get_function_parameter_types(
    function_abi: spec.FunctionABI = None,
    function_signature: typing.Optional[str] = None,
) -> list[spec.ABIDatumType]:

    if function_abi is not None:
        import eth_utils

        output = []
        for item in function_abi.get('inputs', []):
            cast_item = typing.cast(typing.Dict[str, typing.Any], item)
            collapsed = eth_utils.abi.collapse_if_tuple(cast_item)
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

    names = [item.get('name') for item in function_abi.get('inputs', [])]

    if require_names:
        if any(name is None for name in names):
            raise Exception('function abi does not specify names')
        else:
            return typing.cast(typing.List[str], names)
    else:
        return names


def get_function_signature(
    function_abi: spec.FunctionABI = None,
    parameter_types: typing.Optional[list[str]] = None,
    function_name: typing.Optional[str] = None,
    include_names: bool = False,
) -> str:

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

    if function_signature is None:
        function_signature = get_function_signature(function_abi)

    full_hash = hashes.keccak(function_signature.encode(), output_format='raw_hex')
    return full_hash[:8]


def get_function_output_types(
    function_abi: spec.FunctionABI,
) -> list[spec.ABIDatumType]:

    import eth_utils

    output_types = []
    for output in function_abi['outputs']:
        cast_output = typing.cast(typing.Dict[str, typing.Any], output)
        output_type = eth_utils.abi.collapse_if_tuple(cast_output)
        output_types.append(output_type)
    return output_types


def get_function_output_names(
    function_abi: spec.FunctionABI,
    human_readable: bool = False,
) -> list[typing.Optional[str]]:

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

