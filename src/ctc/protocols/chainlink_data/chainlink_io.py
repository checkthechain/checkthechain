import os

import numpy as np
import pandas

from fei import config_utils
from fei.data import directory
from fei.data import web3_utils
from fei.data.etl import etl_list
from fei.data.storage import s3_utils
from . import chainlink_fetch
from . import chainlink_helpers
from . import chainlink_spec


#
# # save data
#


def save_feed_initial_chunk(feed, chunk_size=1000, **export_kwargs):
    """export chainlink data feed from first block to first chunk boundary"""
    start_block = directory.chainlink_feeds_first_blocks[feed]
    end_block = int((start_block + chunk_size) / chunk_size) * chunk_size
    end_block -= 1

    block_range = [start_block, end_block]
    print('exporting', feed, 'initial chunk, range', block_range)
    save_feed(
        feed=feed, start_block=start_block, end_block=end_block, **export_kwargs
    )


def save_feed_all_time(feed, **export_kwargs):
    """export all historical data for a given chainlink data feed"""

    save_feed_initial_chunk(feed, **export_kwargs)
    save_feed_to_present(feed, **export_kwargs)


def save_feed_to_present(
    feed, start_block=None, chunk_size=1000, **export_kwargs
):
    """export all chainlink data feed data since last export"""

    # load current data
    if start_block is None:
        chunk_paths = get_chainlink_chunk_paths(feed)
        end_blocks = [
            int(os.path.splitext(path)[0].split('_')[-1])
            for path in chunk_paths
        ]
        if len(end_blocks) > 0:
            last_saved_block = max(end_blocks)
            start_block = last_saved_block + 1
        else:
            if feed in directory.chainlink_feeds_first_blocks:
                first_block = directory.chainlink_feeds_first_blocks[feed]
            else:
                first_block = chainlink_helpers.find_feed_first_block(feed=feed)
            start_block = int(np.ceil(first_block / chunk_size) * chunk_size)

    # get new block range
    current_block = web3_utils.fetch_latest_block_number()
    end_block = int(current_block / chunk_size) * chunk_size - 1

    save_feed_as_chunks(
        feed=feed,
        start_block=start_block,
        end_block=end_block,
        chunk_size=chunk_size,
        **export_kwargs
    )


def save_feed_as_chunks(
    feed,
    start_block,
    end_block,
    chunk_size=1000,
    chainlink_view=None,
    dry=False,
):
    """export chainlink data feed as chunks"""

    all_chunks = etl_list.get_chunks_in_range(
        start_block=start_block, end_block=end_block, chunk_size=chunk_size
    )

    block_range = [start_block, end_block]
    n = len(all_chunks)
    print('exporting', feed, 'range', block_range, 'as', n, 'chunks')
    print()

    for c, chunk_block_range in enumerate(all_chunks):
        chunk_start_block, chunk_end_block = chunk_block_range
        print('chunk', c + 1, '/', str(n) + ',', chunk_block_range)
        if dry:
            continue
        save_feed(
            feed=feed,
            start_block=chunk_start_block,
            end_block=chunk_end_block,
            chainlink_view=chainlink_view,
        )

    print()
    print('done')


def save_feed(
    feed,
    start_block,
    end_block,
    chainlink_view=None,
    verbose=False,
    if_exists='skip',
    save_to_filesystem=True,
    save_to_sql=False,
    save_to_s3=False,
):
    """export chainlink data feed"""

    kwargs = {
        'feed': feed,
        'start_block': start_block,
        'end_block': end_block,
    }

    # get path
    path = get_chainlink_chunk_path(chainlink_view=chainlink_view, **kwargs)
    if os.path.isfile(path):
        if if_exists == 'skip':
            if verbose:
                print('path already exists: ' + str(path))
            return
        elif if_exists == 'overwrite':
            pass
        elif if_exists == 'raise':
            raise Exception('path already exists: ' + path)
        else:
            raise Exception('unknown if_exists value: ' + str(if_exists))
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if verbose:
        print('retreiving feed data', feed, [start_block, end_block])

    # get data
    data = chainlink_fetch.fetch_feed_data(normalize=False, **kwargs)

    if verbose:
        print('saving feed data:', path)

    # save data
    if save_to_filesystem:
        data.to_csv(path)
    if save_to_sql:
        raise NotImplementedError()
    if save_to_s3:
        s3_utils.upload_to_s3(dataframe=data)

    if verbose:
        print('done')


#
# # load data
#


def load_feed_data(feed):
    """loads all data for a given price feed"""
    paths = get_chainlink_chunk_paths(feed)
    dfs = [pandas.read_csv(path, index_col='block') for path in paths]
    df = pandas.concat(dfs, sort=False)
    df = df.drop_duplicates()
    df = df.sort_index()
    return df


#
# # path functions
#


def get_chainlink_root():
    return os.path.join(
        config_utils.get_config()['data_root'], 'protocols/chainlink',
    )


def list_exported_chainlink_feeds(chainlink_view=None, nonempty=True):
    if chainlink_view is None:
        chainlink_view = 'raw'
    view_dir = os.path.join(get_chainlink_root(), chainlink_view, 'feeds')
    feeds = os.listdir(view_dir)

    if nonempty:
        new_feeds = []
        for feed in feeds:
            feed_path = os.path.join(view_dir, feed)
            if len(os.listdir(feed_path)) > 0:
                new_feeds.append(feed)
        feeds = new_feeds

    return feeds


def get_chainlink_chunk_paths(feed, chainlink_view=None):
    if chainlink_view is None:
        chainlink_view = 'raw'
    feed_dir = os.path.join(get_chainlink_root(), chainlink_view, 'feeds', feed)
    if not os.path.isdir(feed_dir):
        return []
    filenames = os.listdir(feed_dir)
    paths = [
        os.path.join(feed_dir, filename)
        for filename in filenames
        if filename.startswith(feed + '__')
    ]
    paths = sorted(paths)
    return paths


def get_chainlink_chunk_path(
    feed,
    start_block,
    end_block,
    chainlink_view=None,
):
    if chainlink_view is None:
        chainlink_view = 'raw'

    chainlink_root = get_chainlink_root()
    subpath = chainlink_spec.path_templates['feed'].format(
        feed=feed,
        chainlink_view=chainlink_view,
        start_block=start_block,
        end_block=end_block,
    )
    return os.path.join(chainlink_root, subpath)

