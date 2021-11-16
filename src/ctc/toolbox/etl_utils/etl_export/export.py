from ctc import config_utils

from .. import etl_list
from . import export_rows


def export(
    start_block,
    end_block,
    provider=None,
    etl_chunk_root=None,
    etl_backend=None,
    etl_view=None,
    existing_row_datas=None,
    verbose=True,
    exporttypes=None,
    dry=False,
    indent='',
    export_kwargs=None,
):
    if exporttypes is None:
        exporttypes = config_utils.get_config()['default_exporttypes']
    if provider is None:
        provider = config_utils.get_config()['export_provider']
    if etl_view is None:
        etl_view = 'raw'

    kwargs = {
        'provider': provider,
        'start_block': start_block,
        'end_block': end_block,
        'etl_chunk_root': etl_chunk_root,
        'etl_backend': etl_backend,
        'etl_view': etl_view,
        'existing_row_datas': existing_row_datas,
        'verbose': verbose,
        'dry': dry,
        'indent': indent,
    }
    if export_kwargs is not None:
        kwargs.update(export_kwargs)

    paths = {}
    for exporttype in exporttypes:
        if exporttype == 'blocks':
            output = export_rows.export_blocks(**kwargs)
        if exporttype == 'blocks_and_transactions':
            output = export_rows.export_blocks_and_transactions(**kwargs)
        elif exporttype == 'token_transfers':
            output = export_rows.export_token_transfers(**kwargs)
        elif exporttype == 'traces':
            output = export_rows.export_traces(**kwargs)
        elif exporttype == 'receipts_and_logs':
            output = export_rows.export_receipts_and_logs(**kwargs)
        else:
            raise Exception('unknown exporttype:' + str(exporttype))
        paths.update(output)

        if verbose:
            print('\n')

    return paths


def export_as_chunks(
    start_block,
    end_block,
    chunk_size=None,
    verbose=1,
    exporttypes=None,
    **export_kwargs
):

    if exporttypes is None:
        exporttypes = config_utils.get_config()['default_exporttypes']
    if chunk_size is None:
        chunk_size = config_utils.get_config()['export_chunk_size']

    all_chunks = evm.get_chunks_in_range(
        start_block=start_block, end_block=end_block, chunk_size=chunk_size
    )

    inner_verbose = verbose > 1

    if verbose:
        print('exporting from block', start_block, 'to block', end_block)
        print('- chunk_size:', chunk_size)
        print('- n_chunks:', len(all_chunks))
        print('- exporttypes:', exporttypes)
        print()
    for c in range(len(all_chunks)):
        start_block, end_block = all_chunks[c]
        if verbose:
            print(
                'exporting chunk',
                c + 1,
                '/',
                str(len(all_chunks)) + ',',
                'block range [' + str(start_block) + ',',
                str(end_block) + ']',
            )
        export(
            start_block=start_block,
            end_block=end_block,
            verbose=inner_verbose,
            indent='    ',
            exporttypes=exporttypes,
            **export_kwargs
        )

