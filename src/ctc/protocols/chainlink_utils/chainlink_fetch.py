"""

## Resources
- https://docs.chain.link/docs/historical-price-data/
"""

import numpy as np
import pandas
import toolparallel

from ctc import directory
from ctc import evm
from ctc.evm import rpc_utils


aggregator_outputs = [
    'block',
    'roundId',
    'answer',
    'startedAt',
    'updatedAt',
    'answeredInRound',
]


def fetch_feed_datum(
    feed, block=None, format=None, normalize=None, **contract_kwargs
):

    if block is None:
        block = evm.get_block_number('latest')
    if normalize is None:
        normalize = True
    if format is None:
        format = 'dict'
    if feed in directory.chainlink_feeds:
        feed = directory.chainlink_feeds[feed]
    if not evm.is_address_str(feed):
        raise Exception('invalid address: ' + str(feed))

    raw = rpc_utils.eth_call(
        to_address=feed,
        function_name='latestRoundData',
        block=block,
    )

    if normalize:
        name = directory.chainlink_address_to_feed[feed]
        decimals = directory.chainlink_feeds_decimals[name]
        answer_index = 1
        raw = list(raw)
        raw[answer_index] = raw[answer_index] / (10 ** decimals)

    if format == 'full':
        return [block] + raw
    elif format == 'raw':
        return raw
    elif format == 'dict':
        return dict(zip(aggregator_outputs, [block] + raw))
    elif format == 'answer':
        answer_index = 1
        return raw[answer_index]
    else:
        raise Exception('unknown format: ' + str(format))


def fetch_feed_data(
    feed,
    start_block,
    end_block,
    as_dataframe=True,
    remove_redundant=True,
    parallel_kwargs=None,
    **contract_kwargs
):
    """fetch feed data for range of blocks and return as dataframe"""

    # query contract
    blocks = list(range(start_block, end_block + 1))
    if parallel_kwargs is None:
        parallel_kwargs = {}

    common = dict(contract_kwargs, feed=feed, format='full')
    results = toolparallel.parallel_map(
        fetch_feed_datum,
        arg_list=blocks,
        arg_name='block',
        common=common,
        n_workers=60,
    )

    if remove_redundant:
        results = _remove_redundant_data(results)

    if as_dataframe:
        results = pandas.DataFrame(results, columns=aggregator_outputs)
        results.set_index('block', inplace=True)

    return results


def _remove_redundant_data(results):

    if isinstance(results, pandas.DataFrame):
        results = results.iterrows()

    results = [tuple(result) for result in results]

    unique_set = set()
    unique_list = list()
    for result in results:
        tail = result[1:]
        if tail in unique_set:
            continue
        else:
            unique_set.add(tail)
            unique_list.append(result)

    return unique_list


def expand_redundant_data(results, start_block, end_block):
    if not isinstance(results, pandas.DataFrame):
        raise Exception('input should be a dataframe')
    all_blocks = np.arange(start_block, end_block + 1)
    reindexed = results.reindex(all_blocks, fill_value=pandas.NA)
    reindexed = reindexed.fillna(method='ffill')
    return reindexed


def chainlink_chunk(args):
    return fetch_feed_data(*args)


def metaparallel_fetch_feed_data(
    feed_name, start_block, end_block, n_processes=None
):
    """probably delete this after implementing eth batch calls"""

    import multiprocessing

    if n_processes is None:
        n_processes = 4

    bounds = np.linspace(start_block, end_block + 1, n_processes + 1).astype(
        int
    )
    starts, ends = bounds[:-1], bounds[1:]

    pool = multiprocessing.pool.Pool(n_processes)
    arglists = [[feed_name, starts[p], ends[p]] for p in range(n_processes)]
    result = pool.map_async(chainlink_chunk, arglists)
    result = result.get()

    return result

