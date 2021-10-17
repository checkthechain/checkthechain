import os

import toolconfig

import ctc


config_path_env_var = 'CTC_CONFIG'


config_spec = {
    'network': 'Text',
    'data_root': 'Path',
    'fei_abi_dir': 'Path',

    'etl_backend': ['filesystem', 's3', 'sql'],
    'etl_chunk_root_filesystem': 'Path',
    'etl_chunk_root_s3': 'S3URL',
    'export_provider': 'URI',
    'export_chunk_size': 'Integer',
    'default_exporttypes': ['Exporttype'],

    's3_bucket': 'S3BucketName',
    'backup_dir': 'Path',

    'parallel_fetch_config': {
        'n_workers': 'Integer',
        'mode': ['process', 'thread', 'serial', 'nested'],
    },
    'filesystem_layout': 'Map',
    'evm_root': 'Path',
    'etl_root': 'Path',
    'evm_events_path': 'Path',
    'evm_named_contract_abis_path': 'Path',
    'evm_contract_abis_path': 'Path',
}

default_filesystem_layout = {
    'etl_root': '{data_root}/{network}/etl',
    'evm_root': '{data_root}/{network}/evm',
}

default_config_values = {
    'network': 'mainnet',
    'data_root': './data',
    'fei_abi_dir': None,

    'etl_backend': 'filesystem',
    'etl_chunk_root_filesystem': '{data_root}/etl',
    'etl_chunk_root_s3': 's3://fei_analytics/etl',
    'export_provider': None,
    'export_chunk_size': 1000,
    'default_exporttypes': [
        'blocks_and_transactions',
        'token_transfers',
        # 'traces',
    ],

    's3_bucket': None,
    'backup_dir': None,
    'parallel_fetch_config': {},
}
default_config_values.update(default_filesystem_layout)

config_key_variables = {
    'etl_chunk_root_filesystem': ['data_root'],
    'etl_root': ['data_root', 'network'],
    'evm_root': ['data_root', 'network'],
}


def get_config():

    # set default data root to be subdir of package dir
    ctc_root = os.path.dirname(os.path.dirname(ctc.__path__[0]))
    data_root = os.path.join(ctc_root, './data')
    data_root = os.path.abspath(data_root)
    default_config_values_copy = dict(default_config_values)
    default_config_values_copy['data_root'] = data_root

    # get config
    return toolconfig.get_config(
        config_path_env_var=config_path_env_var,
        config_spec=config_spec,
        default_config_values=default_config_values_copy,
        config_key_variables=config_key_variables,
    )

