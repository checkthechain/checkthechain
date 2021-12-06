from ctc import evm


def get_command_spec():
    return {
        'f': add_proxy_abi_comamand,
        'args': [
            {'name': 'contract_address'},
            {'name': 'implementation_address'},
        ],
    }


def add_proxy_abi_comamand(contract_address, implementation_address, **kwargs):
    print('saving proxy contract implementation...')
    print('     for contract:', contract_address)
    print('   implementation:', implementation_address)
    answer = input('continue? ')
    if answer != 'y':
        print('aborting')
        return
    else:
        evm.save_proxy_contract_abi_to_filesystem(
            contract_address=contract_address,
            proxy_implementation=implementation_address,
        )
