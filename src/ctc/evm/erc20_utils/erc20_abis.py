erc20_event_abis = {
    'Transfer': {
        'anonymous': False,
        'inputs': [
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'from',
                'type': 'address',
            },
            {
                'indexed': True,
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
            {
                'indexed': False,
                'internalType': 'uint256',
                'name': 'amount',
                'type': 'uint256',
            },
        ],
        'name': 'Transfer',
        'type': 'event',
    },
}

