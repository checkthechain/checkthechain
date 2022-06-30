from __future__ import annotations

import toolcli
import toolstr

from . import setup_io
from .stages import alias_setup
from .stages import data_dir_setup
from .stages import db_setup
from .stages import network_setup


styles = {
    'header': '#ce93f9 bold',
    'path': '#b9f29f bold',
    'question': '#8be9fd',
    'quote': '#f1fa8c',
    'command': '#64aaaa',
}


async def async_setup_ctc() -> None:

    # print intro
    print('Setting up ctc...')
    print()
    print('Each step is optional')
    print('- by default, setup process will leave existing settings unchanged')
    print('- setup can be rerun multiple times idempotently')
    print()
    toolstr.print(
        'Can skip options by pressing enter at each prompt', style='bold'
    )

    # load old config data for passing to each option
    old_config = setup_io.load_old_config(convert_to_latest=True)
    setup_io.setup_config_path()

    # collect new config file data
    network_data = await network_setup.async_setup_networks(
        old_config=old_config,
        styles=styles,
    )
    data_dir_data = data_dir_setup.setup_data_dir(
        old_config=old_config,
        styles=styles,
    )
    db_data = db_setup.setup_dbs(
        data_dir=data_dir_data['data_dir'],
        network_data=network_data,
        styles=styles,
    )

    # create new config file if need be
    setup_io.write_new_config(
        network_data=network_data,
        db_data=db_data,
        data_dir_data=data_dir_data,
        styles=styles,
    )

    # populate db
    await db_setup.async_populate_db_tables(styles=styles)

    # setup aliases
    alias_setup.add_cli_aliases(styles=styles)

    # finalize
    print()
    print()
    toolstr.print('## Final Steps', style=styles['header'])
    print()
    print('ctc setup compelete')
