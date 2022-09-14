from __future__ import annotations

import toolcli
import toolstr

from ctc import cli
from ctc.protocols import yearn_utils


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_yearn_addresses_command,
        'help': 'output Yearn addresses',
        'args': [
            {
                'name': ['-v', '--verbose'],
                'help': 'output additional addresses',
                'action': 'store_true',
            },
        ],
        'examples': [
            '',
            '-v',
        ],
    }


async def async_yearn_addresses_command(verbose: bool) -> None:
    styles = cli.get_cli_styles()
    toolstr.print_text_box('Yearn Lens Addresses', style=styles['title'])
    print()
    yearn_utils.print_lens_addresses(network='mainnet')
    print()
    print()
    toolstr.print_text_box('Yearn Vault Addresses', style=styles['title'])
    print()
    api_vaults = await yearn_utils.async_get_yearn_api_vaults(network='mainnet')
    yearn_utils.print_vault_addresses(api_vaults=api_vaults, verbose=verbose)
