from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': selector_command,
        'help': '''compute 4byte function selector using function signature

in most cli shells must enclose parentheses in quotes " "''',
        'args': [
            {'name': 'text_signature', 'help': 'signature of function'},
        ],
        'examples': ['"totalSupply()"', '"transfer(address,uint256)"'],
    }


def selector_command(text_signature: str) -> None:
    if '(' not in text_signature and ')' not in text_signature:
        text_signature = text_signature + '()'
    selector = evm.keccak_text(text_signature)[:10]
    print(selector)
