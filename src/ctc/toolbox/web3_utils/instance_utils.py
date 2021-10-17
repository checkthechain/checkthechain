import toolcache
import web3

from ctc import config_utils


@toolcache.cache('memory')
def create_web3_instance(provider=None):
    if provider is None:
        provider = config_utils.get_config()['export_provider']
    if isinstance(provider, str):
        provider = web3.Web3.HTTPProvider(provider)
    return web3.Web3(provider)

