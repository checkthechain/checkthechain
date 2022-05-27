from __future__ import annotations

import toolcli

from ctc import binary


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': selector_command,
        'help': 'compute selector using text function signature',
        'args': [
            {'name': 'text_signature', 'help': 'signature of function'},
        ],
    }


def selector_command(text_signature):
    if '(' not in text_signature and ')' not in text_signature:
        text_signature = text_signature + '()'
    selector = binary.keccak_text(text_signature)[:10]
    print(selector)
