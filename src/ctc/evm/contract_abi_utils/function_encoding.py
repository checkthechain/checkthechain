import eth_abi

from .. import binary_utils
from . import function_parsing


def encode_function_parameters(
    parameters,
    output_format=None,
    parameter_types=None,
    function_signature=None,
    **abi_query,
):

    # get parameter types
    if parameter_types is None:
        parameter_types = function_parsing.get_function_parameter_types(
            function_signature=function_signature,
            n_parameters=len(parameters),
            **abi_query,
        )

    # convert parameter dict to list
    if isinstance(parameters, dict):
        parameter_names = function_parsing.get_function_parameter_names(
            n_parameters=len(parameters), **abi_query
        )
        parameters = (parameters[name] for name in parameter_names)

    # encode
    encoded_bytes = eth_abi.encode_single(
        '(' + ','.join(parameter_types) + ')', parameters
    )

    # convert to output format
    return binary_utils.convert_format(encoded_bytes, output_format)


def encode_call_data(
    *,
    output_format=None,
    function_selector=None,
    parameter_types=None,
    parameters=None,
    encoded_parameters=None,
    **abi_query,
):

    if function_selector is None:
        function_selector = function_parsing.get_function_selector(
            output_format=output_format, **abi_query
        )

    if encoded_parameters is None:
        encoded_parameters = encode_function_parameters(
            parameters=parameters,
            parameter_types=parameter_types,
            output_format=output_format,
            **abi_query,
        )

    function_selector = binary_utils.convert_format(
        function_selector, output_format
    )
    encoded_parameters = binary_utils.convert_format(
        encoded_parameters, output_format
    )

    return function_selector + encoded_parameters


def decode_call_data(call_data, output_format=None):

    call_data_bytes = binary_utils.convert_format(call_data, 'binary')

    function_selector = call_data_bytes[:4]
    function_selector = binary_utils.convert_format(function_selector, 'binary')

    encoded_parameters = call_data_bytes[4:]
    decoded_parameters = decode_function_parameters(encoded_parameters)
    decoded_parameters = binary_utils.convert_format(
        function_selector, 'binary'
    )

    return {
        'function_selector': function_selector,
        'parameters': decoded_parameters,
    }


def decode_function_parameters(encoded_parameters, parameter_types):
    parameter_types_str = '(' + ','.join(parameter_types) + ')'
    encoded_parameters = binary_utils.convert_format(
        encoded_parameters, 'binary'
    )
    parameters = eth_abi.decode_single(parameter_types_str, encoded_parameters)
    return parameters


def decode_function_named_parameters(
    encoded_parameters, parameter_types=None, **abi_query
):
    if parameter_types is None:
        parameter_types = function_parsing.get_function_parameter_types(
            **abi_query
        )
    decoded_parameters = decode_function_parameters(
        encoded_parameters=encoded_parameters,
        parameter_types=parameter_types,
    )
    parameter_names = function_parsing.get_function_parameter_names(**abi_query)
    return {
        parameter_name: parameter
        for parameter_name, parameter in zip(
            parameter_names, decoded_parameters
        )
        if parameter_name is not None
    }


def decode_function_output(encoded_output, output_types=None, **abi_query):
    if output_types is None:
        output_types = function_parsing.get_function_output_types(**abi_query)
    output_types_str = '(' + ','.join(output_types) + ')'
    encoded_output = binary_utils.convert_format(encoded_output, 'binary')
    decoded_output = eth_abi.decode_single(output_types_str, encoded_output)
    return decoded_output

