from __future__ import annotations

import toolcli
import toolstr

from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_chain_command,
        'help': 'display chain_id of provider',
        'args': [
            {'name': 'provider', 'help': 'url or configured name of RPC node'},
            {
                'name': ['--verbose', '-v'],
                'help': 'display additional information about provider chain',
                'action': 'store_true',
            },
            {
                'name': '--config',
                'help': 'display only chain_id from config, not reported chain_id',
                'action': 'store_true',
            },
            {
                'name': '--no-check',
                'help': 'do not check reported chain_id against configured chain_id',
                'action': 'store_true',
            },
        ],
        'examples': [
            'https://rpc.flashbots.net/',
            'https://arbitrumrpc.com',
        ],
    }


async def async_chain_command(
    *,
    provider: str,
    config: bool,
    verbose: bool,
    no_check: bool,
) -> None:

    # gather configured chain_id
    provider_network = None
    config_chain_id = None
    if verbose or config or not no_check:
        try:
            provider_network = rpc.get_provider_network(provider)
            config_chain_id = evm.get_network_chain_id(provider_network)
        except spec.CouldNotDetermineNetwork:
            pass

    # gather reported chain_id
    reported_chain_id = None
    if verbose or not config or not no_check:
        reported_chain_id = await rpc.async_eth_chain_id(provider=provider)

    # print output
    if verbose:
        toolstr.print_text_box('Provider chain information')
        print()

        reported_chain_id = await rpc.async_eth_chain_id(provider=provider)
        toolstr.print_header('Info reported by node')
        print('- chain_id:', reported_chain_id)
        print('- name:', evm.get_network_name(reported_chain_id))
        print()
        toolstr.print_header('Info in config')
        if config_chain_id is None:
            print('[provider not in config]')
        else:
            print('- chain_id:', config_chain_id)
            print('- name:', evm.get_network_name(config_chain_id))

    else:
        if config:
            print(config_chain_id)
        else:
            print(reported_chain_id)

    # perform check
    if not no_check:
        if (
            reported_chain_id is not None
            and config_chain_id is not None
            and reported_chain_id != config_chain_id
        ):
            print()
            raise Exception(
                '[WARNING] configured chain_id is '
                + str(config_chain_id)
                + ' but chain_id reported by node is '
                + str(reported_chain_id)
            )
