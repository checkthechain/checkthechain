from __future__ import annotations

import typing

from ctc import binary
from ctc import spec

from . import contract_parsing
from . import function_parsing


_Parameters = typing.Union[
    typing.Sequence[typing.Any],
    typing.Mapping[str, typing.Any],
]


#
# # call data
#


def encode_call_data(
    *,
    function_selector: typing.Optional[str] = None,
    parameter_types: typing.Optional[spec.ABIDatumType] = None,
    parameters: typing.Optional[_Parameters] = None,
    encoded_parameters: typing.Optional[spec.BinaryData] = None,
    function_abi: typing.Optional[spec.FunctionABI] = None,
) -> str:

    # encode function selector
    if function_selector is None:
        function_selector = function_parsing.get_function_selector(function_abi)
    function_selector = binary.convert(function_selector, 'prefix_hex')

    # encode parameters
    if encoded_parameters is None:
        encoded_parameters = encode_function_parameters(
            parameters=parameters,
            parameter_types=parameter_types,
            function_abi=function_abi,
        )
    encoded_parameters = binary.convert(encoded_parameters, 'raw_hex')

    # join function selector with parameters
    return function_selector + encoded_parameters


def decode_call_data(
    call_data: spec.BinaryData,
    function_abi: typing.Optional[spec.FunctionABI] = None,
    contract_abi: typing.Optional[spec.ContractABI] = None,
) -> spec.DecodedCallData:

    # get function selector
    call_data_bytes = binary.convert(call_data, 'binary')
    function_selector = binary.convert(call_data_bytes[:4], 'prefix_hex')

    # get function abi
    if function_abi is None:
        if contract_abi is None:
            raise Exception('must specify function_abi or contract_abi')
        function_abi = contract_parsing.get_function_abi(
            contract_abi=contract_abi,
            function_selector=function_selector,
        )

    # decode parameters
    encoded_parameters = call_data_bytes[4:]
    parameter_types = function_parsing.get_function_parameter_types(
        function_abi
    )
    decoded_parameters = decode_function_parameters(
        encoded_parameters, parameter_types
    )

    # compute named parameters
    parameter_names = function_parsing.get_function_parameter_names(
        function_abi
    )
    if len(parameter_names) == len(decoded_parameters) and all(
        name is not None for name in parameter_names
    ):
        named_parameters = typing.cast(
            dict[str, typing.Any],
            dict(zip(parameter_names, decoded_parameters)),
        )
    else:
        named_parameters = None

    return {
        'function_abi': function_abi,
        'function_selector': function_selector,
        'parameters': decoded_parameters,
        'named_parameters': named_parameters,
    }


#
# # function parameters
#


def encode_function_parameters(
    parameters: typing.Optional[_Parameters] = None,
    parameter_types: typing.Optional[typing.Sequence[spec.ABIDatumType]] = None,
    function_signature: typing.Optional[str] = None,
    function_abi: typing.Optional[spec.FunctionABI] = None,
) -> bytes:

    if parameters is None:
        return bytes()

    # get parameter types
    if parameter_types is None:
        parameter_types = function_parsing.get_function_parameter_types(
            function_signature=function_signature,
            function_abi=function_abi,
        )

    # convert parameter dict to list
    if isinstance(parameters, typing.Mapping):
        if function_abi is None:
            raise Exception('must specify function_abi')
        parameter_names = function_parsing.get_function_parameter_names(
            function_abi=function_abi,
            require_names=True,
        )
        parameters = [parameters[name] for name in parameter_names]

    # inefficient: convert prefix_hex binary to bytes
    new_parameters = []
    for parameter_type, parameter in zip(parameter_types, parameters):
        if (
            parameter_type == 'bytes32'
            and binary.get_binary_format(parameter) != 'binary'
        ):
            parameter = binary.convert(parameter, 'binary')
        new_parameters.append(parameter)
    parameters = new_parameters

    # encode
    encoded_bytes = binary.abi_encode(
        parameters, '(' + ','.join(parameter_types) + ')'
    )

    # convert to output format
    return encoded_bytes


def decode_function_parameters(
    encoded_parameters: spec.BinaryData,
    parameter_types: list[spec.ABIDatumType],
) -> list[typing.Any]:

    parameter_types_str = '(' + ','.join(parameter_types) + ')'
    encoded_parameters = binary.convert(encoded_parameters, 'binary')
    parameters = binary.abi_decode(encoded_parameters, parameter_types_str)

    return parameters


def decode_function_named_parameters(
    function_abi: spec.FunctionABI,
    encoded_parameters: spec.BinaryData,
    parameter_types: typing.Optional[list[spec.ABIDatumType]] = None,
) -> dict[str, typing.Any]:

    if parameter_types is None:
        parameter_types = function_parsing.get_function_parameter_types(
            function_abi=function_abi,
        )

    decoded_parameters = decode_function_parameters(
        encoded_parameters=encoded_parameters,
        parameter_types=parameter_types,
    )

    # get parameter names
    parameter_names = function_parsing.get_function_parameter_names(
        function_abi
    )

    return {
        parameter_name: parameter
        for parameter_name, parameter in zip(
            parameter_names, decoded_parameters
        )
        if parameter_name is not None
    }


def decode_function_output(
    encoded_output: spec.BinaryData,
    output_types: typing.Optional[list[spec.ABIDatumType]] = None,
    delist_single_outputs: bool = True,
    package_named_outputs: bool = False,
    function_abi: spec.FunctionABI = None,
) -> typing.Any:
    # need to test case when function has no output

    # get output types
    if output_types is None:
        if function_abi is None:
            raise Exception('must specify function_abi')
        output_types = function_parsing.get_function_output_types(function_abi)
    output_types_str = '(' + ','.join(output_types) + ')'

    # decode
    encoded_output = binary.convert(encoded_output, 'binary')
    decoded_output = binary.abi_decode(encoded_output, output_types_str)

    # decode strings
    new_decoded_output = []
    for output_type, item in zip(output_types, decoded_output):
        if output_type == 'string':
            # item = item.decode()
            item = item
        elif output_type == 'bytes32':
            item = binary.convert(item, 'prefix_hex')
        new_decoded_output.append(item)
    decoded_output = new_decoded_output

    # delist
    if delist_single_outputs and len(output_types) == 1:
        decoded_output = decoded_output[0]

    # repackage
    elif package_named_outputs and len(output_types) > 1:
        if function_abi is None:
            raise Exception('must specify function_abi')
        names = function_parsing.get_function_output_names(function_abi)
        if all(name is not None for name in names):
            decoded_output = dict(zip(names, decoded_output))

    return decoded_output

