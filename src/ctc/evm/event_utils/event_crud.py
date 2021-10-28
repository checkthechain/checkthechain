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


def get_events(
    *,
    contract_address,
    start_block=None,
    end_block=None,
    backend_order=None,
    **query
):

    start_block, end_block = block_utils.normalize_block_range(
        contract_address=contract_address,
        start_block=start_block,
        end_block=end_block,
    )

    if backend_order is None:
        backend_order = ['filesystem', 'download']

    return backend_utils.run_on_backend(
        get_backend_functions()['get'],
        contract_address=contract_address,
        start_block=start_block,
        end_block=end_block,
        backend_order=backend_order,
        **query
    )


def save_events(events, **query):
    return backend_utils.run_on_backend(
        get_backend_functions()['save'], events=events, **query
    )


def transfer_events(
    *, contract_address, start_block=None, end_block=None, **query
):

    start_block, end_block = block_utils.normalize_block_range(
        contract_address=contract_address,
        start_block=start_block,
        end_block=end_block,
    )

    return backend_utils.transfer_backends(
        get=get_events,
        save=save_events,
        contract_address=contract_address,
        start_block=start_block,
        end_block=end_block,
        **query
    )


def download_events(
    contract_address,
    event_hash=None,
    event_name=None,
    start_block=None,
    end_block=None,
    verbose=True,
):

    if event_hash is None and event_name is None:
        raise Exception('must specify either event_hash or event_name')

    contract_address = contract_address.lower()

    start_block, end_block = block_utils.normalize_block_range(
        contract_address=contract_address,
        start_block=start_block,
        end_block=end_block,
    )

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
    if listed_events is None:
        download = {'start_block': start_block, 'end_block': end_block}
        downloads.append(download)
    else:

        block_range = listed_events['block_range']
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

