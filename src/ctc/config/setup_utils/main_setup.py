from __future__ import annotations

import toolcli

from . import setup_io
from .stages import data_root_setup
from .stages import db_setup
from .stages import network_setup


styles = {
    'header': '#ce93f9 bold',
    'path': '#b9f29f bold',
    'question': '#8be9fd',
    'quote': '#f1fa8c',
}


def setup_ctc() -> None:

    # print intro
    print('setting up ctc...')
    print()
    print('Tasks:')
    print('- setup config path')
    print('- setup data directory')
    print('- setup networks and providers')
    print()
    print('Each step can be skipped depending on what you need')
    print('- this wizard can be rerun multiple times idempotently')
    print('- by default, wizard will leave current settings unchanged')
    print()
    toolcli.print('Can skip options by simply pressing enter', style='bold')

    # load old config data for passing to each option
    old_config = setup_io.load_old_config(convert_to_latest=True)
    setup_io.setup_config_path()

    # collect new config file data
    network_data = network_setup.setup_networks(styles=styles)
    data_root = data_root_setup.setup_data_root(
        styles=styles,
        old_config=old_config,
    )
    db_data = db_setup.setup_dbs(
        styles=styles,
        data_root=data_root,
        old_config=old_config,
    )

    # create new config file if need be
    setup_io.write_new_config(
        network_data=network_data,
        db_data=db_data,
        data_root=data_root,
        styles=styles,
    )
