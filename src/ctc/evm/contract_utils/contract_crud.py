from ctc.toolbox import web3_utils
from .. import block_utils


def get_contract_creation_block(
    contract_address, start_block=0, end_block='latest',
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
        code = instance.eth.getCode(contract_address, block_identifier=index)
        return len(code) > 0

    return binary_search(
        start_index=start_block,
        end_index=end_block,
        is_match=is_match,
    )


def binary_search(is_match, start_index, end_index):
    """return the first index for which match returns True"""

    while True:
        midpoint = (start_index + end_index) / 2
        midpoint = int(midpoint)

        if is_match(midpoint):
            end_index = midpoint
        else:
            start_index = midpoint

        if start_index + 1 == end_index:
            return end_index
        elif is_match(start_index):
            return start_index
        elif not is_match(end_index):
            return end_index + 1

