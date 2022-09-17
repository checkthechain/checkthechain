from __future__ import annotations

import ast
import re

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': rlp_encode_command,
        'help': 'RLP encode data',
        'args': [
            {
                'name': 'data',
                'help': 'data to encode (can enclose with quotes)',
            },
        ],
        'examples': [
            '1024',
            'cat',
            '0x956f47f50a910163d8bf957cf5846d573e7f87ca',
        ],
    }


def rlp_encode_command(data: str) -> None:

    # quote hex data
    regex = re.compile('0x[0-9a-fA-F]+')
    for match in regex.findall(data):
        data = data.replace(match, '"' + match + '"')

    # convert data to primitive python types
    try:
        parsed = ast.literal_eval(data)
    except ValueError:
        parsed = ast.literal_eval('"""' + data + '"""')

    # rlp encode
    encoded = evm.rlp_encode(parsed)

    # output encoded data
    print(encoded)
