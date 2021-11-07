import toolparallel

from ctc.toolbox import search_utils
from .. import address_utils
from .. import rpc_utils


@toolparallel.parallelize_input(singular_arg='block', plural_arg='blocks')
def get_block(
    block, provider=None, include_full_transactions=False, **rpc_kwargs
):

    # convert to int if not an int or str (e.g. floats or numpy int32)
    if not isinstance(block, (int, str)):
        candidate = int(block)
        if (block - candidate) ** 2 ** 0.5 > 0.001:
            raise Exception()
        block = candidate

    # gather kwargs
    kwargs = dict(
        provider=provider,
        include_full_transactions=include_full_transactions,
        **rpc_kwargs
    )

    # rpc call
    if isinstance(block, int):
        return rpc_utils.eth_get_block_by_number(block_number=block, **kwargs)
    elif isinstance(block, str):
        if block in ['latest', 'earliest', 'pending']:
            return rpc_utils.eth_get_block_by_number(
                block_number=block, **kwargs
            )
        elif block.startswith('0x'):
            if len(block) == 66:
                return rpc_utils.eth_get_block_by_hash(
                    block_hash=block, **kwargs
                )
            else:
                return rpc_utils.eth_get_block_by_number(
                    block_number=block, **kwargs
                )
        elif len(block) == 64:
            return rpc_utils.eth_get_block_by_hash(
                block_hash=block, **kwargs
            )
        elif str.isnumeric(block):
            return rpc_utils.eth_get_block_by_number(
                block_number=int(block), **kwargs
            )
        else:
            raise Exception('unknown block str format: ' + str(block))
    else:
        raise Exception('unknown block specifier: ' + str(block))


def get_block_number(block, provider=None, **rpc_kwargs):

    # gather kwargs
    kwargs = dict(provider=provider, **rpc_kwargs)

    # rpc call
    if block == 'latest':
        return rpc_utils.eth_block_number(**kwargs)
    else:
        return get_block(block=block, **kwargs)['number']


def normalize_block(block, contract_address=None):
    if block is None:
        raise Exception()

    if block == 'latest':
        block = get_block_number('latest')
    if block == 'contract_start':
        block = get_contract_creation_block(contract_address=contract_address)

    return int(block)


def normalize_blocks(blocks, contract_address=None):
    kwargs = {'contract_address': contract_address}

    special = {}
    for block in blocks:
        if block in ['latest', 'earliest', 'pending'] and block not in special:
            special[block] = normalize_block(block, **kwargs)

    normalized = []
    for block in blocks:
        if block in special:
            normalized.append(special[block])
        else:
            normalized.append(normalize_block(block, **kwargs))

    return normalized


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
        latest_block = get_block_number('latest')

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
    start_block=None,
    end_block=None,
    provider=None,
    verbose=True,
):
    """get the block where a contract was created

    algorithm: perform a binary search across blocks, check code bytes in each
    """

    contract_address = address_utils.get_address_checksum(contract_address)

    if start_block is None:
        start_block = 0
    if end_block is None:
        end_block = 'latest'
    if start_block == 'latest' or end_block == 'latest':
        latest_block = get_block_number('latest')
        if start_block == 'latest':
            start_block = latest_block
        if end_block == 'latest':
            end_block = latest_block

    def is_match(index):
        if verbose:
            print('trying block:', index)
        code = rpc_utils.eth_get_code(
            address=contract_address, block_number=index, provider=provider
        )
        return len(code) > 3

    result = search_utils.binary_search(
        start_index=start_block,
        end_index=end_block,
        is_match=is_match,
    )

    if verbose:
        print('result:', result)

    return result

