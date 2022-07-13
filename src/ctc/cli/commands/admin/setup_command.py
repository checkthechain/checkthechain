from __future__ import annotations

import toolcli

help_message = """run ctc setup wizard

setup wizard sets up ctc config and ctc data directory

each step is optional
- by default, setup process will leave existing settings unchanged
- setup can be rerun multiple times idempotently

can run in headless mode (non-interactive mode) using `--headless`:
- headless mode will use the default values for each unspecified parameter
- headless mode is useful in scripts when user input is not possible
- if config file already exists, headless mode must be run with `--overwrite`"""


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_setup_command,
        'help': help_message,
        'args': [
            {
                'name': '--headless',
                'help': 'run in headless mode',
                'action': 'store_true',
            },
            {
                'name': '--ignore-old-config',
                'help': 'ignore settings specified in previous config',
                'action': 'store_true',
            },
            {
                'name': '--skip-networking',
                'help': 'skip network configuration steps',
                'action': 'store_true',
            },
            {
                'name': '--rpc-url',
                'help': 'url to use for RPC node',
            },
            {
                'name': '--rpc-chain-id',
                'help': 'chain id of RPC node given by `--rpc-url`',
                'type': int,
            },
            {
                'name': '--data-dir',
                'help': 'directory where to store ctc data',
            },
            {
                'name': '--disable-logs',
                'help': 'disable ctc logs',
                'action': 'store_true',
            },
            {
                'name': '--skip-db',
                'help': 'skip creating db until it next time it is needed',
                'action': 'store_true',
            },
            {
                'name': '--overwrite',
                'help': 'overwrite old config file',
                'action': 'store_true',
            },
            {
                'name': '--skip-aliases',
                'help': 'disable ctc logs',
                'action': 'store_true',
            },
        ],
        'examples': {
            '': {'skip': True},
            '--headless': {'skip': True},
            '--headless --overwrite': {'skip': True},
        },
    }


async def async_setup_command(
    *,
    headless: bool,
    ignore_old_config: bool,
    skip_networking: bool,
    rpc_url: str | None,
    rpc_chain_id: int | None,
    data_dir: str,
    skip_db: bool,
    disable_logs: bool,
    overwrite: bool,
    skip_aliases: bool,
) -> None:
    from ctc.config import setup_utils

    await setup_utils.async_setup_ctc(
        headless=headless,
        ignore_old_config=ignore_old_config,
        skip_networking=skip_networking,
        rpc_url=rpc_url,
        rpc_chain_id=rpc_chain_id,
        data_dir=data_dir,
        disable_logs=disable_logs,
        skip_db=skip_db,
        overwrite=overwrite,
        skip_aliases=skip_aliases,
    )
