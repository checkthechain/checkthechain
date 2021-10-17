from .. import etl_load
from .. import etl_list
from .. import etl_export


def export_receipts_and_logs_of_transactions(etl_view):
    """export receipts and logs corresponding to a set of transaction chunks

    for each transaction file, ensure that a corresponding log file exists
    """

    # obtain existing paths of transactions and logs
    exported_transactions = etl_list.list_exported_data(
        rowtype='transactions',
        etl_view=etl_view,
    )
    transaction_paths = list(exported_transactions['path_ranges'].keys())
    exported_logs = etl_list.list_exported_data(
        rowtype='logs',
        etl_view=etl_view,
    )
    log_paths = list(exported_logs['path_ranges'].keys())
    log_path_ranges = [
        tuple(item) for item in exported_logs['path_ranges'].values()
    ]

    # determine which block ranges to export
    target_ranges = []
    for transaction_path, path_range in exported_transactions[
        'path_ranges'
    ].items():
        if tuple(path_range) not in log_path_ranges:
            target_ranges.append(path_range)
    n_target_ranges = str(len(target_ranges))
    print('exporting', n_target_ranges, 'chunks of logs:')
    for r, target_range in enumerate(target_ranges):
        print('    ' + str(r + 1) + '.', target_range)

    # export path ranges
    outputs = []
    for r, target_range in enumerate(target_ranges):
        start_block, end_block = target_range

        print()
        print()
        print(
            '(' + str(r + 1),
            '/',
            n_target_ranges + ') exporting logs in block range',
            target_range,
        )
        print()

        # get transaction hashes
        transactions = etl_load.load_data(
            rowtype='transactions',
            start_block=start_block,
            end_block=end_block,
            etl_view=etl_view,
        )
        transaction_hashes = list(transactions['hash'])

        # export log data
        output = etl_export.export(
            exporttypes=['receipts_and_logs'],
            start_block=start_block,
            end_block=end_block,
            etl_view=etl_view,
            export_kwargs={'transaction_hashes': transaction_hashes},
        )
        outputs.append(output)

    print()
    print()
    print('exported all logs')

    return outputs

