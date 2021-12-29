import typing

import toolcli

from ctc import spec
from ctc import directory_new as directory
from ctc.toolbox import nested_utils
from .. import config_read


class _NetworkData(typing.TypedDict):
    default_network: spec.NetworkName
    networks: dict[spec.NetworkName, spec.NetworkMetadata]
    providers: dict[spec.ProviderName, spec.ProviderSpec]


def setup_networks(styles: dict[str, str]) -> tuple[_NetworkData, bool]:
    print()
    print()
    toolcli.print('## Network Setup', style=styles['header'])

    print()
    print('The following networks are already installed:')
    default_networks = directory.load_networks_from_disk(use_default=True)
    for network_name, network_metadata in default_networks.items():
        print('-', network_name)

    # add new networks
    networks: dict[spec.NetworkName, spec.NetworkMetadata] = {}
    while toolcli.input_yes_or_no(
        '\nWould you like to add additional networks?',
        style=styles['question'],
        default='no',
    ):
        name = toolcli.input_prompt('Network name? ', style=styles['question'])
        network_id = toolcli.input_int('Network id? ', style=styles['question'])
        block_explorer = toolcli.input_prompt(
            'Network explorer? ', style=styles['question']
        )
        if name in networks:
            print('Overwriting network with name', name)
        networks[name] = {
            'name': name,
            'network_id': network_id,
            'block_explorer': block_explorer,
        }

    # set default network
    choices_set = set(networks.keys()) | set(default_networks.keys())
    choices = sorted(choices_set)
    print()
    default_network_index = toolcli.input_number_choice(
        prompt='Which network to use as default?',
        choices=choices,
        default='mainnet',
        style=styles['question'],
    )
    default_network = choices[default_network_index]

    # get providers
    providers: dict[spec.ProviderName, spec.ProviderSpec]
    providers = typing.cast(dict[spec.ProviderName, spec.ProviderSpec], {})

    data: _NetworkData = {
        'networks': networks,
        'default_network': default_network,
        'providers': providers,
    }

    if config_read.config_path_exists() and config_read.config_is_valid():
        old_config = config_read.get_config()
        old_data = {key: old_config.get(key) for key in data.keys()}
        create_new_config = not nested_utils.is_equal(data, old_data)
    else:
        create_new_config = True

    return data, create_new_config


# def setup_providers() -> tuple[
#     dict[spec.NetworkReference, spec.ProviderSpec], bool
# ]:
#     # TODO: check if networks are known and valid
#     if config_read.config_exists():
#         config = config_read.get_config()
#     else:
#         config = None

#     if config is not None:
#         old_providers = config.get('providers')
#         if not isinstance(old_providers, list):
#             print()
#             print('Current config value of providers is invaild')

#         if len(providers) > 0:
#             print()
#             print('Current providers in config:')
#             for network, provider in config['providers'].items():
#                 print('-', network + ':', provider)
#         else:
#             print()
#             print('No providers currently specified in config')
#     else:
#         print('Would you like to add a provider?')
#         print()

#     print()
#     print('Would you like to add more providers? ')


# def setup_default_network() -> tuple[spec.NetworkName, bool]:
#     if config_read.config_exists():
#         config = config_read.get_config()
#     else:
#         config = None


# def setup_network_metadata() -> bool:
#     pass

