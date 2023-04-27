from __future__ import annotations

import typing

import toolstr
import toolcli

import ctc
from . import setup_io
from .stages import alias_setup
from .stages import data_dir_setup
from .stages import db_setup
from .stages import network_setup
from .stages import cli_setup


styles: toolcli.StyleTheme = {
    'title': '#ce93f9 bold',
    'description': '#b9f29f bold',
    'metavar': '#8be9fd',
    'content': '#f1fa8c',
    'option': '#64aaaa',
    'comment': '#6272a4',
}


async def async_setup_ctc(
    *,
    headless: bool = False,
    ignore_old_config: bool = False,
    skip_networking: bool = False,
    rpc_url: str | None = None,
    rpc_chain_id: int | None = None,
    data_dir: str | None = None,
    disable_logs: bool = False,
    skip_db: bool = False,
    overwrite: bool = True,
    skip_aliases: bool = False,
) -> None:

    # print intro
    toolstr.print('# Setting up ctc...', style=styles['title'])
    print()
    toolstr.print(
        'Running setup process for ctc '
        + toolstr.add_style(ctc.__version__, styles['description'] + ' bold')
    )
    if not ctc.__version__.split('.')[-1].isnumeric():
        print('(this is not a stable release, use pypi for stable releases)')
    print()
    print('Each step is optional')
    print('- by default, setup process will leave existing settings unchanged')
    print('- setup can be rerun multiple times idempotently')
    print()
    toolstr.print(
        'Can skip options by pressing enter at each prompt', style='bold'
    )

    # load old config data for passing to each option
    if ignore_old_config:
        old_config: typing.Mapping[typing.Any, typing.Any] = {}
    else:
        old_config = setup_io.load_old_config(convert_to_latest=True)
    setup_io.setup_config_path()

    # collect new config file data
    network_data = await network_setup.async_setup_networks(
        skip_networking=skip_networking,
        rpc_url=rpc_url,
        rpc_chain_id=rpc_chain_id,
        old_config=old_config,
        styles=styles,
        headless=headless,
    )
    data_dir_data = data_dir_setup.setup_data_dir(
        old_config=old_config,
        styles=styles,
        headless=headless,
        default_data_dir=data_dir,
        disable_logs=disable_logs,
    )
    cli_data = cli_setup.setup_cli(
        old_config=old_config,
        styles=styles,
        headless=headless,
    )
    if not skip_db:
        db_data = db_setup.setup_dbs(
            data_dir=data_dir_data['data_dir'],
            network_data=network_data,
            styles=styles,
            headless=headless,
            old_db_configs=old_config.get('db_configs'),
        )
    else:
        from ctc.config import config_defaults

        db_data = {
            'db_configs': config_defaults.get_default_db_configs(
                data_dir=data_dir_data['data_dir']
            ),
        }

    # create new config file if need be
    setup_io.write_new_config(
        network_data=network_data,
        db_data=db_data,
        data_dir_data=data_dir_data,
        cli_data=cli_data,
        styles=styles,
        headless=headless,
        overwrite=overwrite,
    )

    # populate db
    if not skip_db:
        await db_setup.async_populate_db_tables(
            db_config=db_data['db_configs']['main'],
            styles=styles,
        )

    # setup aliases
    alias_setup.add_cli_aliases(
        styles=styles,
        headless=headless,
        skip_aliases=skip_aliases,
    )

    # finalize
    print()
    print()
    toolstr.print('## Final Steps', style=styles['title'])
    print()
    print('ctc setup complete')
