from __future__ import annotations

import toolcli
import toolstr

from ctc import cli
from ctc import evm
from ctc import spec
from ctc import rpc


help_message = """register custom proxy implementation of a contract

Implementation ABI will be downloaded for original contract

Manual registration using this command is normally unnecessary

This command is useful for custom proxy implementations"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_proxy_add_command,
        'help': help_message,
        'args': [
            {
                'name': 'proxy_contract',
                'help': 'contract that falls back to other contract',
            },
            {
                'name': 'implementation_contract',
                'help': 'contract that implements proxy contract',
            },
            {
                'name': '--confirm',
                'help': 'confirm registration of proxy',
                'action': 'store_true',
            },
        ],
        'examples': [
            '0xfb558ecd2d24886e8d2956775c619deb22f154ef 0xe16db319d9da7ce40b666dd2e365a4b8b3c18217 --confirm',
        ],
    }


async def async_proxy_add_command(
    proxy_contract: spec.Address,
    implementation_contract: spec.Address,
    *,
    confirm: bool,
) -> None:

    styles = cli.get_cli_styles()

    provider = rpc.get_provider()
    network = evm.get_network_name(provider['network'])

    if not confirm:
        toolstr.print(
            'Registering ABI implementation for use with proxy contract...',
            style=styles['description'],
        )
        toolstr.print(
            '             proxy '
            + toolstr.add_style(proxy_contract, styles['metavar']),
            style=styles['option'],
        )
        toolstr.print(
            '    implementation '
            + toolstr.add_style(implementation_contract, styles['metavar']),
            style=styles['option'],
        )
        toolstr.print(
            '           network '
            + toolstr.add_style(str(network), styles['metavar']),
            style=styles['option'],
        )
        print()
        answer = toolcli.input_yes_or_no(
            'Proceed? (y/n) ', style=styles['metavar']
        )
        if not answer:
            return

    abi = await evm.async_get_contract_abi(
        contract_address=proxy_contract,
        network=network,
        proxy_implementation=implementation_contract,
        db_query=False,
    )

    print('resulting abi contains', len(abi), 'items')
