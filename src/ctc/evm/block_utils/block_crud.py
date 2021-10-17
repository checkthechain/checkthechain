from ctc.toolbox import web3_utils


def fetch_latest_block(web3_instance=None, provider=None):
    if web3_instance is None:
        web3_instance = web3_utils.create_web3_instance(provider=provider)
    return web3_instance.eth.getBlock('latest')


def fetch_latest_block_number(provider=None):
    block = fetch_latest_block(provider=provider)
    return block['number']

