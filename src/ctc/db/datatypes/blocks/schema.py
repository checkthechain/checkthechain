import toolsql


def get_schema() -> toolsql.DBSchema:
    return {
        'tables': {
            'blocks': {
                'columns': [
                    {
                        'name': 'number',
                        'type': 'Integer',
                        'primary': True,
                    },
                    {
                        'name': 'base_fee_per_gas',
                        'type': 'Text',
                    },
                    {
                        'name': 'difficulty',
                        'type': 'Text',
                    },
                    {
                        'name': 'extra_data',
                        'type': 'Text',
                    },
                    {
                        'name': 'gas_limit',
                        'type': 'Text',
                    },
                    {
                        'name': 'gas_used',
                        'type': 'Text',
                    },
                    {
                        'name': 'hash',
                        'type': 'Text',
                    },
                    {
                        'name': 'logs_bloom',
                        'type': 'Text',
                    },
                    {
                        'name': 'miner',
                        'type': 'address',
                    },
                    {
                        'name': 'nonce',
                        'type': 'Text',
                    },
                    {
                        'name': 'parent_hash',
                        'type': 'Text',
                    },
                    {
                        'name': 'receipts_root',
                        'type': 'Text',
                    },
                    {
                        'name': 'sha3_uncles',
                        'type': 'Text',
                    },
                    {
                        'name': 'size',
                        'type': 'Text',
                    },
                    {
                        'name': 'state_root',
                        'type': 'Text',
                    },
                    {
                        'name': 'timestamp',
                        'type': 'Text',
                    },
                    {
                        'name': 'total_difficulty',
                        'type': 'Text',
                    },
                    {
                        'name': 'transactions',
                        'type': 'JSON',
                    },
                    {
                        'name': 'transactions_root',
                        'type': 'Text',
                    },
                    {
                        'name': 'uncles',
                        'type': 'JSON',
                    },
                ],
            },
        },
    }

