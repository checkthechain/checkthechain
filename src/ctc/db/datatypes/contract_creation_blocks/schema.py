import toolsql


def get_schema() -> toolsql.DBSchema:
    return {
        'tables': {
            'contract_creation_blocks': {
                'columns': [
                    {
                        'name': 'address',
                        'type': 'Text',
                        'primary': True,
                    },
                    {
                        'name': 'block_number',
                        'type': 'Integer',
                        'index': True,
                    },
                ],
            },
        },
    }

