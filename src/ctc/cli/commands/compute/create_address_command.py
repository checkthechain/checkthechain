from __future__ import annotations

import toolcli

from ctc import evm


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': create_address_command,
        'help': 'generate address in the style of CREATE or CREATE2',
        'args': [
            {'name': 'sender', 'help': 'sender address'},
            {
                'name': 'nonce_or_salt',
                'help': 'sender nonce (for CREATE) or salt (for CREATE2)',
            },
            {
                'name': 'init_code',
                'nargs': '?',
                'help': 'initialization bytecode for CREATE2',
            },
        ],
        'examples': [
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 123',
            '0xd8da6bf26964af9d7eed9e03e53415d37aa96045 0xaabb 0xaabbccdd',
        ],
    }


def create_address_command(
    *,
    sender: str,
    nonce_or_salt: str,
    init_code: str,
) -> None:
    if init_code is not None:
        address = evm.get_created_address(
            sender=sender, salt=nonce_or_salt, init_code=init_code
        )
    else:
        address = evm.get_created_address(
            sender=sender, nonce=int(nonce_or_salt)
        )
    print(address)
