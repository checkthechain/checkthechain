from .. import binary_utils
from . import function_parsing


#
# # call data
#


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
        parameter_format = binary_utils.get_binary_format(function_selector)
        if parameter_format == 'prefix_hex':
            parameter_format = 'raw_hex'
        encoded_parameters = encode_function_parameters(
            parameters=parameters,
            parameter_types=parameter_types,
            output_format=parameter_format,
            **abi_query,
        )

    return function_selector + encoded_parameters


def decode_call_data(call_data, output_format=None, **abi_query):

    call_data_bytes = binary_utils.convert_binary_format(call_data, 'binary')

    function_selector = call_data_bytes[:4]
    function_selector = binary_utils.convert_binary_format(
        function_selector, 'binary'
    )

    encoded_parameters = call_data_bytes[4:]
    parameter_types = function_parsing.get_function_parameter_types(
        function_selector=function_selector, **abi_query
    )
    decoded_parameters = decode_function_parameters(
        encoded_parameters, parameter_types
    )
    parameter_names = function_parsing.get_function_parameter_names(
        function_selector=function_selector, **abi_query
    )
    if len(parameter_names) == len(decoded_parameters):
        decoded_parameters = dict(zip(parameter_names, decoded_parameters))

    if output_format is None:
        output_format = 'prefix_hex'
    function_selector = binary_utils.convert_binary_format(
        function_selector, output_format
    )

    return {
        'function_selector': function_selector,
        'parameters': decoded_parameters,
    }


#
# # function parameters
#


def encode_function_parameters(
    parameters,
    output_format=None,
    parameter_types=None,
    function_signature=None,
    **abi_query,
):
    if parameters is None:
        return binary_utils.convert_binary_format(
            '0x', output_format=output_format
        )
    else:
        n_parameters = len(parameters)

    # get parameter types
    if parameter_types is None:
        parameter_types = function_parsing.get_function_parameter_types(
            function_signature=function_signature,
            n_parameters=n_parameters,
            **abi_query,
        )

    # convert parameter dict to list
    if isinstance(parameters, dict):
        parameter_names = function_parsing.get_function_parameter_names(
            n_parameters=n_parameters, **abi_query
        )
        parameters = [parameters[name] for name in parameter_names]

    # encode
    encoded_bytes = binary_utils.encode_evm_data(
        '(' + ','.join(parameter_types) + ')', parameters
    )

    # convert to output format
    return binary_utils.convert_binary_format(encoded_bytes, output_format)


def decode_function_parameters(encoded_parameters, parameter_types):
    parameter_types_str = '(' + ','.join(parameter_types) + ')'
    encoded_parameters = binary_utils.convert_binary_format(
        encoded_parameters, 'binary'
    )
    parameters = binary_utils.decode_evm_data(
        parameter_types_str, encoded_parameters
    )
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


def decode_function_output(
    encoded_output,
    output_types=None,
    delist_single_outputs=True,
    package_named_results=False,
    **abi_query,
):
    # need to test case when function has no output

    # get output types
    if output_types is None:
        output_types = function_parsing.get_function_output_types(**abi_query)
    output_types_str = '(' + ','.join(output_types) + ')'

    # decode
    encoded_output = binary_utils.convert_binary_format(
        encoded_output, 'binary'
    )
    decoded_output = binary_utils.decode_evm_data(
        output_types_str, encoded_output
    )

    # decode strings
    if 'string' in output_types:
        string_decoded_output = []
        for output_type, item in zip(output_types, decoded_output):
            if output_type == 'string':
                item = item.decode()
            string_decoded_output.append(item)
        decoded_output = string_decoded_output

    # delist
    if delist_single_outputs and len(output_types) == 1:
        decoded_output = decoded_output[0]

    # repackage
    elif package_named_results and len(output_types) > 1:
        names = function_parsing.function_function_output_names(**abi_query)
        if names is not None:
            decoded_output = dict(zip(names, decoded_output))

    return decoded_output

