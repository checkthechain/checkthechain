from ctc.toolbox import backend_utils
from .event_backends import filesystem_events
from .event_backends import node_events
from .. import block_utils


def get_backend_functions():
    return {
        'get': {
            'filesystem': filesystem_events.get_events_from_filesystem,
            'download': download_events,
            'node': node_events.get_events_from_node,
        },
        'save': {
            'filesystem': filesystem_events.save_events_to_filesystem,
        },
    }


def get_events(**query):
    backend_order = query.get('backend_order')
    if backend_order is None:
        backend_order = ['filesystem', 'download']
        query['backend_order'] = backend_order
    return backend_utils.run_on_backend(get_backend_functions()['get'], **query)


def save_events(events, **query):
    query['events'] = events
    return backend_utils.run_on_backend(
        get_backend_functions()['save'], **query
    )


def transfer_events(**kwargs):
    return backend_utils.transfer_backends(
        get=get_events, save=save_events, **kwargs
    )


def download_events(
    start_block,
    end_block,
    contract_address,
    event_hash=None,
    event_name=None,
    verbose=True,
):

    if start_block == 'latest' or end_block == 'latest':
        latest_block = block_utils.fetch_latest_block_number()
        if start_block == 'latest':
            start_block = latest_block
        if end_block == 'latest':
            end_block = latest_block

    # get event hash
    if event_hash is None:
        event_hash = filesystem_events._event_name_to_event_hash(
            event_name=event_name, contract_address=contract_address
        )

    # determine what needs to be downloaded
    listed_events = filesystem_events.list_events(
        contract_address=contract_address,
        event_hash=event_hash,
    )
    downloads = []
    if event_hash not in listed_events:
        download = {'start_block': start_block, 'end_block': end_block}
        downloads.append(download)
    else:

        block_range = listed_events[event_hash]['block_range']
        if start_block < block_range[0]:
            download = {
                'start_block': start_block,
                'end_block': block_range[0] - 1,
                'common_kwargs': {'verbose': verbose},
            }
            downloads.append(download)
        if end_block > block_range[-1]:
            download = {
                'start_block': block_range[-1] + 1,
                'end_block': end_block,
                'common_kwargs': {'verbose': verbose},
            }
            downloads.append(download)

    # perform downloads
    for download in downloads:
        transfer_events(
            from_backend='node',
            to_backend='filesystem',
            event_hash=event_hash,
            contract_address=contract_address,
            **download
        )

    # load from filesystem
    return filesystem_events.get_events_from_filesystem(
        event_hash=event_hash,
        contract_address=contract_address,
        start_block=start_block,
        end_block=end_block,
    )

