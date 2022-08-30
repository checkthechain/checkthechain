from __future__ import annotations

import os
import typing

from ctc import spec


def get_config_validators() -> typing.Mapping[
    str, None | typing.Callable[..., None]
]:
    return {
        'config_spec_version': validate_config_spec_version,
        'data_dir': validate_data_dir,
        'networks': validate_networks,
        'providers': validate_providers,
        'default_network': validate_default_network,
        'default_providers': validate_default_providers,
        'db_configs': validate_db_configs,
        'log_rpc_calls': None,
        'log_sql_queries': None,
    }


def get_config_base_types() -> typing.Mapping[
    str, typing.Type[typing.Any] | tuple[typing.Type[typing.Any], ...]
]:
    return {
        'config_spec_version': str,
        'data_dir': str,
        'networks': dict,
        'providers': dict,
        'default_network': (int, type(None)),
        'default_providers': dict,
        'db_configs': dict,
        'log_rpc_calls': bool,
        'log_sql_queries': bool,
    }


def validate_config(config: typing.Mapping[typing.Any, typing.Any]) -> None:
    """raise spec.ConfigInvalid if config is not valid"""

    config_validators = get_config_validators()
    config_base_types = get_config_base_types()

    # check that all required keys are present
    for key in spec.config_keys:
        if key not in config:
            raise spec.ConfigInvalid('config does not specify key: ' + str(key))

    # check that each entry is valid
    for key, value in config.items():

        # check that key is allowed
        if key not in spec.config_keys:
            raise spec.ConfigInvalid('key not allowed in config:')

        # check value type
        if not isinstance(value, config_base_types[key]):
            message = 'invalid type for ' + str(key) + ': ' + str(value)
            raise spec.ConfigInvalid(message)

    # check additional key validations
    for key, value in config.items():
        key_validator = config_validators.get(key)
        if key_validator is not None:
            key_validator(value=value, config=config)


def is_valid_config(config: typing.Mapping[typing.Any, typing.Any]) -> bool:
    try:
        validate_config(config)
        return True
    except spec.ConfigInvalid:
        return False


#
# # individual validators
#


def validate_config_spec_version(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:
    pieces = value.split('.')
    if len(pieces) != 3:
        raise spec.ConfigInvalid('invalid config_spec_version: ' + str(value))
    if not all(piece.isnumeric() for piece in pieces):
        raise spec.ConfigInvalid('invalid config_spec_version: ' + str(value))

    if pieces[0] != '0' or pieces[1] != '3':
        raise spec.ConfigInvalid('config must use a version 0.3.x')


def validate_data_dir(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:
    abspath = os.path.abspath(os.path.expanduser(value))
    if value != abspath:
        raise spec.ConfigInvalid(
            'data_dir path should be absolute: ' + str(value)
        )


def validate_networks(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:
    config_keys = {'name', 'chain_id', 'block_explorer'}
    for chain_id, network_metadata in value.items():
        if not isinstance(chain_id, int):
            raise spec.ConfigInvalid(
                'networks should be identified by int chain_id'
            )
        if set(network_metadata.keys()) != config_keys:
            raise spec.ConfigInvalid(
                'network_metadata should specify name, chain_id, and block_explorer, instead got: '
                + str(list(network_metadata.keys()))
            )

        name = network_metadata['name']
        block_explorer = network_metadata['block_explorer']
        if name is not None and not isinstance(name, str):
            raise spec.ConfigInvalid('network name is not a str')
        if network_metadata['chain_id'] != chain_id:
            raise spec.ConfigInvalid('chain_id does not match')
        if block_explorer is not None and not isinstance(block_explorer, str):
            raise spec.ConfigInvalid('block_explorer is not a str')


def validate_providers(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:

    provider_keys = set(spec.provider_keys)
    for provider_name, provider in value.items():
        if not isinstance(provider_name, str):
            raise spec.ConfigInvalid('provider name should be a str')

        if set(provider.keys()) != provider_keys:
            raise spec.ConfigInvalid(
                'provider should have keys: ' + str(provider_keys)
            )

        url = provider['url']
        name = provider['name']
        network = provider['network']
        protocol = provider['protocol']
        session_kwargs = provider['session_kwargs']
        chunk_size = provider['chunk_size']

        if not isinstance(url, str):
            raise spec.ConfigInvalid('provider url must be a str')
        if name != provider_name:
            raise spec.ConfigInvalid('provider name does not match')
        if not isinstance(network, int):
            raise spec.ConfigInvalid(
                'provider networks should be an int chain_id'
            )
        if network not in config['networks']:
            raise spec.ConfigInvalid('provider network not in network entries')
        if protocol != 'http':
            raise spec.ConfigInvalid('only http supported')
        if not isinstance(session_kwargs, dict):
            raise spec.ConfigInvalid('session_kwargs must be a dict')
        if chunk_size is not None and not isinstance(chunk_size, int):
            raise spec.ConfigInvalid('chunk_size is not int')

        if not url.startswith('http'):
            raise spec.ConfigInvalid(
                'http provider url must start with "http://" or "https://"'
            )


def validate_default_network(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:

    if value is None:
        return

    # check that value is present in networks
    networks = config['networks']
    if value not in networks:
        raise spec.ConfigInvalid('default_network not in networks entries')


def validate_default_providers(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:

    networks = config['networks']
    providers = config['providers']
    for chain_id, provider_name in value.items():
        if chain_id not in networks:
            raise spec.ConfigInvalid(
                'chain_id in default_providers not present in network entries'
            )
        if provider_name not in providers:
            raise spec.ConfigInvalid(
                'provider in default_providers not present in provider entries'
            )


def validate_db_configs(
    value: typing.Any, config: typing.Mapping[typing.Any, typing.Any]
) -> None:

    if set(value.keys()) != {'main'}:
        raise spec.ConfigInvalid(
            'db_configs should only have main entry for now'
        )
    if set(value['main'].keys()) != {'dbms', 'path'}:
        raise spec.ConfigInvalid('db config should have keys dbms and path')
