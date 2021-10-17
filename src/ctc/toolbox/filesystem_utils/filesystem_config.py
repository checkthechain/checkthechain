import os

from fei import config_utils


def get_scrape_root():
    config = config_utils.get_config()
    return os.path.join(config['data_root'], 'scrape')


def setup_event_scrape_dirs():
    scrape_root = get_scrape_root()
    os.makedirs(scrape_root, exist_ok=True)
    for datatype in ['events', 'contract_abis']:
        os.makedirs(os.path.join(scrape_root, datatype), exist_ok=True)
    print('all scrape dirs created')

