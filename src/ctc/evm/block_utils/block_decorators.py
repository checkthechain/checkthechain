import toolparallel

from ctc import config_utils


def parallelize_block_fetching(config=None, **kwargs):

    # parallel_fetch_config = config_utils.get_config()['parallel_fetch_config']
    parallel_fetch_config = {}
    if config is None:
        config = {}
    config = dict(parallel_fetch_config, **config)

    parallel_kwargs = {
        'singular_arg': 'block',
        'plural_arg': 'blocks',
        'config': config,
    }
    parallel_kwargs.update(kwargs)
    return toolparallel.parallelize_input(**parallel_kwargs)

