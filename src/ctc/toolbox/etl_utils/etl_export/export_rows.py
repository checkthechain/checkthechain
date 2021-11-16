import os
import subprocess
import tempfile

from .. import etl_list
from .. import etl_spec


def export_blocks(
    provider,
    start_block,
    end_block,
    etl_chunk_root=None,
    etl_backend=None,
    etl_view=None,
    overwrite=False,
    verbose=True,
    existing_row_datas=None,
    dry=False,
    indent='',
):

    # set output paths
    kwargs = {
        'start_block': start_block,
        'end_block': end_block,
        'etl_chunk_root': etl_chunk_root,
        'etl_backend': etl_backend,
        'etl_view': etl_view,
    }
    blocks_path = etl_list.get_path('blocks', **kwargs)
    paths = {'blocks': blocks_path}

    # build command
    command = etl_spec.command_templates['blocks'].format(
        provider=provider,
        start_block=start_block,
        end_block=end_block,
        blocks_path=blocks_path,
    )

    skip = _should_skip_export(
        exporttype='blocks',
        overwrite=overwrite,
        existing_row_datas=existing_row_datas,
        paths=paths,
        start_block=start_block,
        end_block=end_block,
    )

    # run command
    if verbose:
        print(indent + 'exporting blocks')
    if skip:
        print(indent + 'files already exist, skipping')
        return paths
    if not dry:
        subprocess.call(command, shell=True)
    if verbose:
        print(indent + 'done')
        print()
        print(indent + 'exported blocks to:', blocks_path)

    return paths


def export_blocks_and_transactions(
    provider,
    start_block,
    end_block,
    etl_chunk_root=None,
    etl_backend=None,
    etl_view=None,
    overwrite=False,
    verbose=True,
    existing_row_datas=None,
    dry=False,
    indent='',
):

    # set output paths
    kwargs = {
        'start_block': start_block,
        'end_block': end_block,
        'etl_chunk_root': etl_chunk_root,
        'etl_backend': etl_backend,
        'etl_view': etl_view,
    }
    blocks_path = etl_list.get_path('blocks', **kwargs)
    transactions_path = etl_list.get_path('transactions', **kwargs)
    paths = {'blocks': blocks_path, 'transactions': transactions_path}

    # build command
    command = etl_spec.command_templates['blocks_and_transactions'].format(
        provider=provider,
        start_block=start_block,
        end_block=end_block,
        blocks_path=blocks_path,
        transactions_path=transactions_path,
    )

    skip = _should_skip_export(
        exporttype='blocks_and_transactions',
        overwrite=overwrite,
        existing_row_datas=existing_row_datas,
        paths=paths,
        start_block=start_block,
        end_block=end_block,
    )

    # run command
    if verbose:
        print(indent + 'exporting blocks and transactions')
    if skip:
        print(indent + 'files already exist, skipping')
        return paths
    if not dry:
        subprocess.call(command, shell=True)
    if verbose:
        print(indent + 'done')
        print()
        print(indent + 'exported blocks to:', blocks_path)
        print(indent + 'exported transactions to:', transactions_path)

    return paths


def export_token_transfers(
    provider,
    start_block,
    end_block,
    etl_chunk_root=None,
    etl_backend=None,
    etl_view=None,
    verbose=True,
    overwrite=False,
    existing_row_datas=None,
    dry=False,
    indent='',
):

    kwargs = {
        'start_block': start_block,
        'end_block': end_block,
        'etl_chunk_root': etl_chunk_root,
        'etl_backend': etl_backend,
        'etl_view': etl_view,
    }
    token_transfers_path = etl_list.get_path('token_transfers', **kwargs)
    paths = {'token_transfers': token_transfers_path}

    # build command
    command = etl_spec.command_templates['token_transfers'].format(
        provider=provider,
        start_block=start_block,
        end_block=end_block,
        token_transfers_path=token_transfers_path,
    )

    skip = _should_skip_export(
        exporttype='token_transfers',
        overwrite=overwrite,
        existing_row_datas=existing_row_datas,
        paths=paths,
        start_block=start_block,
        end_block=end_block,
    )

    if verbose:
        print(indent + 'exporting token transfers')
    if skip:
        print(indent + 'files already exist, skipping')
        return paths
    if not dry:
        subprocess.call(command, shell=True)
    if verbose:
        print(indent + 'done')
        print()
        print(indent + 'exported token transfers to:', token_transfers_path)

    return paths


def export_traces(
    provider,
    start_block,
    end_block,
    etl_chunk_root=None,
    etl_backend=None,
    etl_view=None,
    verbose=True,
    overwrite=False,
    existing_row_datas=None,
    dry=False,
    indent='',
):

    kwargs = {
        'start_block': start_block,
        'end_block': end_block,
        'etl_chunk_root': etl_chunk_root,
        'etl_backend': etl_backend,
        'etl_view': etl_view,
    }
    traces_path = etl_list.get_path('traces', **kwargs)
    paths = {'traces': traces_path}

    command = etl_spec.command_templates['traces'].format(
        start_block=start_block,
        end_block=end_block,
        provider=provider,
        traces_path=traces_path,
    )

    skip = _should_skip_export(
        exporttype='traces',
        overwrite=overwrite,
        existing_row_datas=existing_row_datas,
        paths=paths,
        start_block=start_block,
        end_block=end_block,
    )

    if verbose:
        print(indent + 'exporting traces')
    if skip:
        print(indent + 'files already exist, skipping')
        return paths
    if not dry:
        subprocess.call(command, shell=True)
    if verbose:
        print(indent + 'done')
        print()
        print(indent + 'exported traces to:', traces_path)

    return paths


def export_receipts_and_logs(
    provider,
    start_block,
    end_block,
    transaction_hashes_path=None,
    transaction_hashes=None,
    etl_chunk_root=None,
    etl_backend=None,
    etl_view=None,
    verbose=True,
    overwrite=False,
    existing_row_datas=None,
    dry=False,
    indent='',
):

    kwargs = {
        'start_block': start_block,
        'end_block': end_block,
        'etl_chunk_root': etl_chunk_root,
        'etl_backend': etl_backend,
        'etl_view': etl_view,
    }

    if transaction_hashes is None and transaction_hashes_path is None:
        raise Exception('must specify transaction_hashes somehow')
    if transaction_hashes is not None:
        (_, transaction_hashes_path) = tempfile.mkstemp()
        with open(transaction_hashes_path, 'w') as f:
            f.write('\n'.join(transaction_hashes))
    receipts_path = etl_list.get_path('receipts', **kwargs)
    logs_path = etl_list.get_path('logs', **kwargs)
    paths = {'receipts': receipts_path, 'logs': logs_path}

    command = etl_spec.command_templates['receipts_and_logs'].format(
        provider=provider,
        transaction_hashes_path=transaction_hashes_path,
        receipts_path=receipts_path,
        logs_path=logs_path,
    )

    skip = _should_skip_export(
        exporttype='receipts_and_logs',
        overwrite=overwrite,
        existing_row_datas=existing_row_datas,
        paths=paths,
        start_block=start_block,
        end_block=end_block,
    )
    if verbose:
        print(indent + 'exporting receipts and logs')
    if skip:
        print(indent + 'files already exist, skipping')
        return paths
    if not dry:
        subprocess.call(command, shell=True)
    if verbose:
        print(indent + 'done')
        print()
        print(indent + 'exported receipts to:', receipts_path)
        print(indent + 'exported logs to:', logs_path)

    return paths


#
# # helper functions
#


def _should_skip_export(
    exporttype,
    overwrite,
    start_block,
    end_block,
    existing_row_datas=None,
    paths=None,
):
    """skip export only if all rowtypes not accounted for in existing data

    check either by providing existing_row_datas or paths
    """

    if overwrite:
        return False

    rowtypes = etl_spec.rowtypes_of_exporttypes[exporttype]

    if existing_row_datas is not None:
        for rowtype in rowtypes:
            row_data = existing_row_datas[rowtype]
            mask_index = row_data['mask_index']
            start_index = mask_index.index(start_block)
            end_index = mask_index.index(end_block) + 1
            block_counts = row_data['block_counts']
            if not (block_counts[start_index:end_index] > 0).all():
                return False
        else:
            return True

    if paths is not None:
        for rowtype in rowtypes:
            if not os.path.isfile(paths[rowtype]):
                return False
        return True

    else:
        raise Exception('must provide either existing_row_datas or paths')

