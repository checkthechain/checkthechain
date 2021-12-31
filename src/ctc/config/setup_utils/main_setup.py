from ctc import spec

from . import config_path_setup
from . import data_root_setup
from . import final_setup
from . import network_setup
from . import validation_setup


styles = {
    'header': '#ce93f9 bold',
    'path': '#b9f29f bold',
    'question': '#8be9fd',
    'quote': '#f1fa8c',
}


def setup_ctc() -> None:

    # print intro
    print('ctc initializing...')
    print()
    print('This process will make sure each of the following is completed:')
    print('- setup config path')
    print('- setup data directory')
    print('- setup networks and providers')
    print()
    print('Each step can be skipped depending on what you need')

    # ensure file is valid
    validation_setup.ensure_valid(styles=styles)

    # collect new config file data
    (
        config_path,
        create_because_config_path,
    ) = config_path_setup.setup_config_path(styles=styles)
    data_root, create_because_data_root = data_root_setup.setup_data_root(styles=styles)
    network_data, create_because_networks = network_setup.setup_networks(
        styles=styles
    )

    # TODO: prompt whether to keep any other old config settings
    pass

    # create new config file if need be
    create_new_config = any(
        [
            create_because_config_path,
            create_because_data_root,
            create_because_networks,
        ]
    )

    config: spec.ConfigSpec = {
        'version': '0.1.0',
        'data_dir': data_root,
        'networks': network_data['networks'],
        'providers': network_data['providers'],
        'network_defaults': network_data['network_defaults'],
    }

    final_setup.finalize_setup(
        create_new_config=create_new_config,
        config_path=config_path,
        config=config,
        styles=styles,
    )

