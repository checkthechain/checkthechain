from __future__ import annotations

import os
import typing
import urllib.parse

import toolcli
import toolstr

from ctc import rpc
from ctc import spec
from ... import config_defaults


async def async_setup_networks(
    *,
    old_config: typing.Mapping[typing.Any, typing.Any],
    headless: bool,
    rpc_url: str | None,
    rpc_chain_id: int | None,
    skip_networking: bool = False,
    styles: typing.Mapping[str, str],
) -> spec.PartialConfig:

    if skip_networking:
        providers = old_config.get('providers')
        if providers is None:
            providers = {}

        networks = old_config.get('networks')
        if networks is None:
            networks = config_defaults.get_default_networks_metadata()

        default_network = old_config.get('default_network')

        default_providers = old_config.get('default_providers')
        if default_providers is None:
            default_providers = {}

        return {
            'providers': providers,
            'networks': networks,
            'default_network': default_network,
            'default_providers': default_providers,
        }

    print()
    print()
    toolstr.print('## Network Setup', style=styles['header'])
    print()

    # get providers
    providers, networks = await async_specify_providers(
        old_config=old_config,
        styles=styles,
        headless=headless,
        rpc_url=rpc_url,
        rpc_chain_id=rpc_chain_id,
    )

    # get additional custom networks
    networks = specify_networks(
        networks=networks,
        styles=styles,
        headless=headless,
    )

    # get default network
    default_network = specify_default_network(
        providers=providers,
        networks=networks,
        styles=styles,
        headless=headless,
        rpc_url=rpc_url,
    )

    # get default providers
    default_providers = specify_default_providers(
        providers=providers,
        networks=networks,
        styles=styles,
        headless=headless,
    )

    print()
    print('Network setup complete')

    # return results
    data: spec.PartialConfig = {
        'providers': providers,
        'networks': networks,
        'default_network': default_network,
        'default_providers': default_providers,
    }
    return data


async def async_specify_providers(
    *,
    old_config: typing.Mapping[str, typing.Any],
    headless: bool,
    rpc_url: str | None,
    rpc_chain_id: int | None,
    styles: typing.Mapping[str, str],
) -> tuple[
    typing.Mapping[str, spec.Provider],
    typing.MutableMapping[spec.ChainId, spec.NetworkMetadata],
]:

    providers: typing.MutableMapping[str, spec.Provider] = {}
    networks: typing.MutableMapping[spec.ChainId, spec.NetworkMetadata] = dict(
        config_defaults.get_default_networks_metadata()
    )

    # add providers first, then configure their networks if those are unknown
    old_providers = old_config.get('providers', {})
    if len(old_providers) > 0:
        print('Currently using these providers:')
        for provider_name, provider_metadata in old_providers.items():
            toolstr.print(
                '-',
                provider_name,
                '['
                + styles['path']
                + ']'
                + provider_metadata['url']
                + '[/'
                + styles['path']
                + ']',
            )
        print()
        answer = toolcli.input_yes_or_no(
            'Would you like to continue using these providers? ',
            style=styles['question'],
            default='yes',
            headless=headless,
        )
        if answer:
            # TODO: validate old_providers
            providers.update(old_providers)

    if rpc_url is not None:
        await async_collect_provider_metadata(
            providers=providers,
            networks=networks,
            styles=styles,
            url=rpc_url,
            chain_id=rpc_chain_id,
            headless=headless,
        )
    elif len(providers) == 0:
        print()
        print('Most ctc operations require an RPC provider')
        print()
        prompt = 'Would you like to specify an RPC provider? '
        if toolcli.input_yes_or_no(
            prompt=prompt,
            style=styles['question'],
            default='yes',
            headless=headless,
        ):
            await async_collect_provider_metadata(
                providers=providers,
                networks=networks,
                styles=styles,
                headless=headless,
                url=None,
                chain_id=None,
            )

    # collect additional providers
    if len(providers) > 0:
        answer = toolcli.input_yes_or_no(
            prompt='Would you like to specify additional RPC providers? ',
            style=styles['question'],
            default='no',
            headless=headless,
        )
        while answer:

            # collect provider
            await async_collect_provider_metadata(
                providers=providers,
                networks=networks,
                styles=styles,
                headless=False,
                url=None,
                chain_id=None,
            )

            # prompt for additional providers
            answer = toolcli.input_yes_or_no(
                prompt='Would you like to specify additional RPC providers? ',
                style=styles['question'],
                default='no',
                headless=False,
            )

    return providers, networks


async def async_collect_provider_metadata(
    *,
    providers: typing.MutableMapping[str, spec.Provider],
    networks: typing.MutableMapping[spec.ChainId, spec.NetworkMetadata],
    styles: typing.Mapping[str, str],
    headless: bool,
    url: str | None,
    chain_id: int | None,
) -> None:
    """collect metadata for a provider"""

    print()
    if url is None:

        if os.environ.get('ETH_RPC_URL') not in [None, '']:
            default_url = os.environ['ETH_RPC_URL']
        else:
            default_url = None

        if headless and default_url is None:
            raise Exception(
                'if using headless mode, must either specify --rpc-url or set the ETH_RPC_URL env var'
            )

        url = toolcli.input_prompt(
            'What is the RPC provider URL? ',
            style=styles['question'],
            allow_blank=False,
            default=default_url,
            headless=headless,
        )
    else:
        print('Adding RPC provider: ' + str(url))

    if url.startswith('ws://'):
        # TODO: take new input instead of raising exception
        raise NotImplementedError('websockets not supported')
    elif not url.startswith('https://') and not url.startswith('http://'):
        print()
        print('No prefix for url. Adding `https://`')
        url = 'https://' + url

    if (
        chain_id is None
        and url == os.environ.get('ETH_RPC_URL')
        and os.environ.get('ETH_RPC_CHAIN_ID') not in [None, '']
    ):
        try:
            chain_id = int(os.environ['ETH_RPC_CHAIN_ID'])
            print(
                'could not use value of ETH_RPC_CHAIN_ID, not a valid integer'
            )
        except Exception:
            pass

    if chain_id is None:
        try:
            temporary_provider: spec.Provider = {
                'name': None,
                'network': -2,
                'protocol': 'http',
                'session_kwargs': {},
                'chunk_size': None,
                'url': url,
                'convert_reverts_to_none': False,
            }
            try:
                chain_id = await rpc.async_eth_chain_id(
                    provider=temporary_provider
                )
            except Exception:
                chain_id = toolcli.input_int(
                    'Could not connect to RPC provider. What is this provider\'s chain_id? ',
                    style=styles['question'],
                    headless=False,
                )
            description = 'chain_id = ' + str(chain_id)
            if chain_id in networks:
                name = networks[chain_id]['name']
                if name is not None:
                    description = description + ', network = ' + name
            print('Provider using: ' + description)
        except Exception as e:
            raise e
            print('Could not query node for chain_id metadata')
            chain_id = toolcli.input_int(
                'What is the chain_id used by this node? ',
                style=styles['question'],
                headless=False,
            )

    # determine whether chain_id is of known network
    known_network = any(
        chain_id == network.get('chain_id') for network in networks.values()
    )

    # if chain_id of unknown network, collect network metadata
    if not known_network:
        if headless:
            raise NotImplementedError(
                'cannot use unknown network in headless mode'
            )
        collect_network_metadata(
            chain_id=chain_id,
            networks=networks,
            styles=styles,
        )

    name = toolcli.input_prompt(
        prompt='What should this node be called? ',
        default=create_default_provider_name(url=url, network=chain_id),
        style=styles['question'],
        headless=headless,
    )
    if url.startswith('http'):
        protocol: typing.Literal['http'] = 'http'
    else:
        raise Exception('unknown protocol, missing http(s) in url?')
    provider: spec.Provider = {
        'name': name,
        'url': url,
        'network': chain_id,
        'protocol': protocol,
        'session_kwargs': {},
        'chunk_size': None,
        'convert_reverts_to_none': False,
    }
    providers[name] = provider


def create_default_provider_name(url: str, network: int) -> str:
    hostname = urllib.parse.urlparse(url).hostname
    if hostname is not None:
        hostname_pieces = hostname.split('.')
        if len(hostname_pieces) == 1:
            hostname_piece = hostname_pieces[0]
        else:
            hostname_piece = hostname_pieces[-2]
    else:
        hostname_piece = url

    return hostname_piece + '__' + str(network)


def collect_network_metadata(
    *,
    styles: typing.Mapping[str, str],
    networks: typing.MutableMapping[spec.ChainId, spec.NetworkMetadata],
    name: str | None = None,
    chain_id: int | None = None,
) -> None:
    """collect metadata for a network"""

    if chain_id is None:
        chain_id = toolcli.input_int(
            'What is the network\'s chain_id? (enter a blank line to go back)\n',
            style=styles['question'],
        )
        # CHECK that chain_id is not already taken
    if name is None:
        name = toolcli.input_prompt(
            'What is the network\'s name? (enter a blank line to go back)\n',
            style=styles['question'],
        )
        # CHECK that name is not already taken

    block_explorer = toolcli.input_prompt(
        'Network block explorer? ', style=styles['question']
    )
    network_metadata: spec.NetworkMetadata = {
        'name': name,
        'chain_id': chain_id,
        'block_explorer': block_explorer,
    }
    networks[chain_id] = network_metadata


def specify_networks(
    *,
    networks: typing.MutableMapping[spec.ChainId, spec.NetworkMetadata],
    styles: typing.Mapping[str, str],
    headless: bool,
) -> typing.MutableMapping[spec.ChainId, spec.NetworkMetadata]:

    # print current networks
    print()
    print('Have metadata for the following networks:')
    print()
    rows = [
        [networks[chain_id]['name'], chain_id]
        for chain_id in sorted(networks.keys())
    ]
    toolstr.print_table(
        rows,
        labels=['name', 'chain_id'],
        border=styles['comment'],
        label_style=styles['header'],
        column_styles={
            'name': styles['question'],
            'chain_id': styles['path'],
        },
        add_row_index=True,
    )

    # add new networks
    while toolcli.input_yes_or_no(
        '\nWould you like to add metadata for additional networks? ',
        style=styles['question'],
        default='no',
        headless=headless,
    ):
        collect_network_metadata(
            styles=styles,
            networks=networks,
        )

    print()
    print('Using', len(networks), 'networks in config')

    return networks


def specify_default_network(
    *,
    networks: typing.Mapping[spec.ChainId, spec.NetworkMetadata],
    providers: typing.Mapping[str, spec.Provider],
    styles: typing.Mapping[str, str],
    headless: bool,
    rpc_url: str | None,
) -> spec.ChainId:

    # set default network
    choices_set = [
        str(network['name']) + ' (chain_id = ' + str(network['chain_id']) + ')'
        for network in networks.values()
    ]
    choices = sorted(choices_set)

    # only consider given provider if rpc_url is present
    if rpc_url is not None:
        providers = {
            provider_name: provider
            for provider_name, provider in providers.items()
            if provider['url'] == rpc_url
        }

    # determine default choice
    default: str | None = None
    if len(providers) == 1:
        provider = list(providers.values())[0]
        network = provider.get('network')
        for network_metadata in networks.values():
            if (
                isinstance(network, int)
                and network == network_metadata['chain_id']
            ) or (
                isinstance(network, str) and network == network_metadata['name']
            ):
                default = (
                    str(network_metadata['name'])
                    + ' (chain_id = '
                    + str(network_metadata['chain_id'])
                    + ')'
                )
                break
    elif len(providers) > 1:
        for provider in providers.values():
            if provider.get('network') in [1, 'mainnet']:
                default = 'mainnet (chain_id = 1)'

    print()
    default_network_index = toolcli.input_number_choice(
        prompt='Which network to use as default?',
        choices=choices,
        default=default,
        style=styles['question'],
        headless=headless,
    )

    # clean this horrorshow up
    return int(choices[default_network_index].split(' ')[-1].strip(')'))


def specify_default_providers(
    *,
    networks: typing.Mapping[spec.ChainId, spec.NetworkMetadata],
    providers: typing.Mapping[str, spec.Provider],
    styles: typing.Mapping[str, str],
    headless: bool,
) -> typing.Mapping[spec.ChainId, spec.ProviderName]:

    # compile providers for each network
    providers_per_network: dict[int, list[str]] = {}
    for provider_name, provider_metadata in providers.items():
        network = provider_metadata['network']
        if network is None:
            raise Exception(
                'unknown network for provider: ' + str(provider_metadata)
            )
        if not isinstance(network, int):
            for chain_id, network_metadata in networks.items():
                if network_metadata['name'] == network:
                    network = chain_id
                    break
            else:
                raise Exception(
                    'could not determine chain_id for network: ' + str(network)
                )
        providers_per_network.setdefault(network, [])
        providers_per_network[network].append(provider_name)

    # get default provider for each network
    default_providers = {}
    for network in providers_per_network:
        n_providers = len(providers_per_network[network])
        if n_providers == 1:
            default_providers[network] = providers_per_network[network][0]
        elif n_providers > 1:
            prompt = (
                'Which provider to use as default for '
                + str(networks[network]['name'])
                + ' (chain_id = '
                + str(network)
                + ')?'
            )
            answer = toolcli.input_number_choice(
                prompt=prompt,
                choices=providers_per_network[network],
                style=styles['question'],
                headless=headless,
            )
            default_providers[network] = providers_per_network[network][answer]

    return default_providers
