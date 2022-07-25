from __future__ import annotations

import ast
import json
import os
import subprocess
import tempfile
import typing

import pytest

import ctc
from ctc import spec
from ctc.config import config_defaults
from ctc.config import upgrade_utils


#
# # utility functions
#


def run_ctc_command(
    subcommand: str | typing.Sequence[str],
    max_time: int | None = 30,
    **cli_args: typing.Any,
) -> str:

    if isinstance(subcommand, str):
        subcommand = [subcommand]

    # assemble command pieces
    command_pieces = ['python3', '-m', 'ctc'] + list(subcommand)
    for key, value in cli_args.items():

        if value is False:
            continue

        command_pieces.append('--' + key.replace('_', '-'))
        if isinstance(value, str):
            command_pieces.append(value)
        elif value is True:
            pass
        elif isinstance(value, int):
            command_pieces.append(str(value))
        else:
            raise Exception('arg values should be True or str')
    command_pieces = [
        piece.strip('"') for piece in command_pieces if piece != ''
    ]

    # run command
    print('running command: ' + ' '.join(command_pieces))
    output = subprocess.check_output(
        command_pieces, timeout=max_time, env=os.environ.copy()
    )
    return output.decode().rstrip('\n')


def run_ctc_headless(
    max_time: int | None = 30,
    ignore_old_config=True,
    skip_aliases=True,
    **cli_args: typing.Any,
) -> typing.Any:

    return run_ctc_command(
        subcommand='setup',
        max_time=max_time,
        headless=True,
        ignore_old_config=ignore_old_config,
        skip_aliases=skip_aliases,
        **cli_args,
    )


def get_ctc_config() -> typing.Mapping[typing.Any]:
    output = run_ctc_command('config', json=True)
    return ast.literal_eval(output)


def get_default_provider() -> spec.Provider:
    config = get_ctc_config()
    default_network = config['default_network']
    default_provider = config['default_providers'][default_network]
    return config['providers'][default_provider]


def get_rpc_urls():
    config = get_ctc_config()
    return [provider['url'] for provider in config['providers'].values()]


def create_temp_config_path():
    tempdir = tempfile.mkdtemp()
    return os.path.join(tempdir, 'config.json')


def get_db_path():
    config = get_ctc_config()
    return config['db_configs']['main']['path']


#
# # tests
#


def test_use_env_var_config_path(monkeypatch):
    # test that ctc reads from the CTC_CONFIG_PATH env var
    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)
    actual = run_ctc_command(['config', 'path'])
    assert config_path == actual


def test_ctc_setup__env_var_sets_config_path(monkeypatch):
    # test that ctc writes to the CTC_CONFIG_PATH env var
    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)
    assert not os.path.isfile(config_path)
    run_ctc_headless(skip_networking=True)
    assert os.path.isfile(config_path)


def test_ctc_setup__requires_rpc(monkeypatch):
    # test that ctc runs into headless exception
    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)
    if 'ETH_RPC_URL' in os.environ:
        monkeypatch.delenv('ETH_RPC_URL')
    with pytest.raises(Exception):
        run_ctc_headless(skip_db=True)


def test_ctc_setup__with_env_eth_rpc_url(monkeypatch):
    # test that ctc setup can use ETH_RPC_URL

    # requires internet to run properly

    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)

    test_url = 'https://some/test/url'

    # set rpc in env var
    monkeypatch.setenv('ETH_RPC_URL', test_url)
    monkeypatch.setenv('ETH_RPC_CHAIN_ID', '3')

    # perform setup
    run_ctc_headless(skip_db=True)

    # ensure that newly written config file has specified rpc
    default_provider = get_default_provider()
    assert test_url == default_provider['url']
    assert 3 == default_provider['network']


def test_ctc_setup__with_rpc_command(monkeypatch):
    # test that ctc setup can use rpc-url

    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)

    test_url = 'https://some/test/url'
    test_chain_id = '10'

    # perform setup
    if 'ETH_RPC_URL' in os.environ:
        monkeypatch.delenv('ETH_RPC_URL')
    run_ctc_headless(
        rpc_url=test_url,
        rpc_chain_id=test_chain_id,
        skip_db=True,
    )

    # ensure that newly written config file has specified rpc
    default_provider = get_default_provider()
    assert test_url == default_provider['url']
    assert int(test_chain_id) == default_provider['network']


def test_ctc_setup__set_data_dir(monkeypatch):

    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)

    data_dir = tempfile.mkdtemp()
    assert len(os.listdir(data_dir)) == 0
    run_ctc_headless(
        data_dir=data_dir,
        rpc_url='https://some/test/url',
        rpc_chain_id=1,
    )
    assert len(os.listdir(data_dir)) > 0


def test_ctc_setup__skip_db(monkeypatch):
    # test that skipping or not skipping db setup works properly

    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)

    data_dir = tempfile.mkdtemp()
    run_ctc_headless(
        data_dir=data_dir,
        skip_db=True,
        rpc_url='https://some/test/url',
        rpc_chain_id=1,
    )

    db_path = get_db_path()
    assert db_path.startswith(data_dir)
    assert not os.path.isfile(db_path)

    # now rerun without skipping db, and assert that db is created
    run_ctc_headless(
        data_dir=data_dir,
        skip_db=False,
        rpc_url='https://some/test/url',
        rpc_chain_id=1,
    )
    assert os.path.isfile(db_path)


old_config__0_2_10 = {
    'config_spec_version': '0.2.10',
    'data_dir': '/home/storm/ctc_data',
    'providers': {
        'example_provider_1': {
            'url': 'https://example_provider.com',
            'name': 'example_provider_1',
            'network': 1,
            'protocol': 'http',
            'session_kwargs': {},
            'chunk_size': None,
            'convert_reverts_to_none': False,
        },
        'example_provider_2': {
            'url': 'http://localhost',
            'name': 'example_provider_2',
            'network': 42161,
            'protocol': 'http',
            'session_kwargs': {},
            'chunk_size': None,
            'convert_reverts_to_none': False,
        },
    },
    'networks': {
        'mainnet': {
            'name': 'mainnet',
            'chain_id': 1,
            'block_explorer': 'etherscan.io',
        },
        'arbitrum': {
            'name': 'arbitrum',
            'chain_id': 42161,
            'block_explorer': 'arbiscan.io',
        },
    },
    'network_defaults': {
        'default_network': 'mainnet',
        'default_providers': {
            'mainnet': 'example_provider_1',
            'arbitrum': 'example_provider_2',
        },
    },
}


default_config = config_defaults.get_default_config()

old_config_examples = [
    #
    # 0.2.10 style config
    old_config__0_2_10,
    #
    # blank old config
    {},
    #
    # 0.3.0 style default config
    default_config,
    #
    # default config with small changes
    dict(
        default_config,
        data_dir=tempfile.mkdtemp(),
        providers={},
        default_provider=None,
    ),
]


@pytest.mark.parametrize('old_config', old_config_examples)
def test_ctc_setup__use_old_config(monkeypatch, old_config):
    # test that
    # 1) values are preserved from old_configs
    # 2) old_configs do not crash the setup

    config_path = create_temp_config_path()
    monkeypatch.setenv('CTC_CONFIG_PATH', config_path)

    # write old config to config path
    assert not os.path.isfile(config_path)
    with open(config_path, 'w') as f:
        json.dump(old_config, f)

    # run setup
    run_ctc_headless(
        skip_networking=True,
        ignore_old_config=False,
        overwrite=True,
        skip_db=True,
    )

    old_config_upgraded = upgrade_utils.upgrade_config(old_config)

    # now, check that old_config values are preserved if they were valid
    new_config = get_ctc_config()

    # check that current ctc value is used
    assert new_config['config_spec_version'] == ctc.__version__

    # check that providers are preserved
    assert len(old_config_upgraded['providers']) == len(new_config['providers'])

    # check that default network is preserved
    assert (
        old_config_upgraded.get('default_network')
        == new_config['default_network']
    )

    # check that default providers are preserved
    assert len(old_config_upgraded['default_providers']) == len(
        new_config['default_providers']
    )
    for key, value in old_config_upgraded['default_providers'].items():
        assert new_config['default_providers'].get(key) == value

    # check that custom networks are preserved
    old_networks = old_config_upgraded.get('networks')
    if old_networks is not None:
        for network_id, network_metadata in old_networks.items():
            assert network_id in new_config['networks']
            for key, value in network_metadata.items():
                assert new_config['networks'][network_id].get(key) == value

    # check that data dir is preserved
    old_data_dir = old_config_upgraded.get('data_dir')
    if old_data_dir is not None:
        assert new_config['data_dir'] == old_data_dir
