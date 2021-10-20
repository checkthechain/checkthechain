from ctc.toolbox import search_utils
from ctc.toolbox import web3_utils
from .. import block_utils


def get_contract_creation_block(
    contract_address,
    start_block=0,
    end_block='latest',
    verbose=True,
):
    """
    algorithm: perform a binary search across blocks, check code bytes in each
    """

    instance = web3_utils.create_web3_instance()

    if start_block == 'latest' or end_block == 'latest':
        latest_block = block_utils.fetch_latest_block_number()
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

