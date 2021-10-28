from ctc.toolbox import web3_utils
from ctc.toolbox import search_utils
from .. import address_utils


def fetch_latest_block(web3_instance=None, provider=None):
    if web3_instance is None:
        web3_instance = web3_utils.create_web3_instance(provider=provider)
    return web3_instance.eth.getBlock('latest')


def fetch_latest_block_number(provider=None):
    block = fetch_latest_block(provider=provider)
    return block['number']


def normalize_block(block, contract_address=None):
    if block is None:
        raise Exception()

    if block == 'latest':
        block = fetch_latest_block_number()
    if block == 'contract_start':
        block = get_contract_creation_block(contract_address=contract_address)

    return int(block)


def normalize_block_range(start_block, end_block, contract_address=None):
    """fill in special values and defaults for block range

    - must fill in dynamic 'latest' values when using a range in multiple calls
    """

    # fill in default values
    if start_block is None:
        if contract_address is not None:
            start_block = 'contract_start'
        else:
            start_block = 'latest'
    if end_block is None:
        end_block = 'latest'

    # fill in special values
    if 'contract_start' in [start_block, end_block]:
        contract_start = get_contract_creation_block(
            contract_address=contract_address
        )
    if 'latest' in [start_block, end_block]:
        latest_block = fetch_latest_block_number()

    # assign special values
    if start_block == 'latest':
        start_block = latest_block
    if start_block == 'contract_start':
        start_block = contract_start
    if end_block == 'latest':
        end_block = latest_block
    if end_block == 'contract_start':
        end_block = contract_start

    # convert to int
    start_block = int(start_block)
    end_block = int(end_block)

    return (start_block, end_block)


def get_contract_creation_block(
    contract_address,
    start_block=0,
    end_block='latest',
    verbose=True,
):
    """get the block where a contract was created

    algorithm: perform a binary search across blocks, check code bytes in each
    """

    contract_address = address_utils.get_address_checksum(contract_address)
    instance = web3_utils.create_web3_instance()

    if start_block == 'latest' or end_block == 'latest':
        latest_block = fetch_latest_block_number()
        if start_block == 'latest':
            start_block = latest_block
        if end_block == 'latest':
            end_block = latest_block

    def is_match(index):
        if verbose:
            print('trying block:', index)
        code = instance.eth.getCode(contract_address, block_identifier=index)
        return len(code) > 0

    result = search_utils.binary_search(
        start_index=start_block,
        end_index=end_block,
        is_match=is_match,
    )

    if verbose:
        print('result:', result)

    return result

