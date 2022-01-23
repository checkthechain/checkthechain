filesystem_layout = {
    'evm_events_path': 'events/contract__{contract_address}/event__{event_hash}/{start_block}__to__{end_block}.csv',
    'evm_contract_abis_path': 'contract_abis/contract__{contract_address}/{name}.json',
    'evm_named_contract_abis_path': '{data_root}/{network}/evm/named_contract_abis',
}


erc20_abis = {
    'name': {
        'constant': True,
        'inputs': [],
        'name': 'name',
        'outputs': [{'name': '', 'type': 'string'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'approve': {
        'constant': False,
        'inputs': [
            {'name': '_spender', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'},
        ],
        'name': 'approve',
        'outputs': [{'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'totalSupply': {
        'constant': True,
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'transferFrom': {
        'constant': False,
        'inputs': [
            {'name': '_from', 'type': 'address'},
            {'name': '_to', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'},
        ],
        'name': 'transferFrom',
        'outputs': [{'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'decimals': {
        'constant': True,
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint8'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'balanceOf': {
        'constant': True,
        'inputs': [{'name': '_owner', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': 'balance', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'symbol': {
        'constant': True,
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'name': '', 'type': 'string'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'transfer': {
        'constant': False,
        'inputs': [
            {'name': '_to', 'type': 'address'},
            {'name': '_value', 'type': 'uint256'},
        ],
        'name': 'transfer',
        'outputs': [{'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function',
    },
    'allowance': {
        'constant': True,
        'inputs': [
            {'name': '_owner', 'type': 'address'},
            {'name': '_spender', 'type': 'address'},
        ],
        'name': 'allowance',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function',
    },
    'Approval': {
        'anonymous': False,
        'inputs': [
            {'indexed': True, 'name': 'owner', 'type': 'address'},
            {'indexed': True, 'name': 'spender', 'type': 'address'},
            {'indexed': False, 'name': 'value', 'type': 'uint256'},
        ],
        'name': 'Approval',
        'type': 'event',
    },
    'Transfer': {
        'anonymous': False,
        'inputs': [
            {'indexed': True, 'name': 'from', 'type': 'address'},
            {'indexed': True, 'name': 'to', 'type': 'address'},
            {'indexed': False, 'name': 'value', 'type': 'uint256'},
        ],
        'name': 'Transfer',
        'type': 'event',
    },
}

