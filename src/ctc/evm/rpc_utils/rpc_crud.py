import random
import re

from .. import binary_utils


#
# # rpc creation
#

def construct_rpc_call(method, parameters):
    return {
        'jsonrpc': '2.0',
        'method': method,
        'params': parameters,
        'id': random.randint(1, 1e18),
    }


#
# # rpc coding
#

def encode_rpc_block(block):
    if block in ['latest', 'earliest', 'pending']:
        return block
    else:
        return binary_utils.convert_binary_format(block, 'prefix_hex')


def decode_rpc_map(result, quantities=None):
    if quantities is None:
        quantities = {}
    decoded = {}
    for key, value in result.items():
        if key in quantities:
            value = binary_utils.convert_binary_format(value, 'integer')
        decoded[key] = value
    return decoded


def rpc_keys_to_snake_case(map):
    """

    not for general usage beyond the keys that appear in the EVM rpc spec

    adapted from https://stackoverflow.com/a/1176023
    """
    return {
        re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower(): value
        for key, value in map.items()
    }

