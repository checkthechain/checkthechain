from ctc.toolbox import backend_utils
from . import contract_abi_backends


def get_backend_functions():
    return {
        'get': {
            'filesystem': contract_abi_backends.get_contract_abi_from_filesystem,
            'download': download_contract_abi,
            'etherscan': contract_abi_backends.get_contract_abi_from_etherscan,
        },
        'save': {
            'filesystem': contract_abi_backends.save_contract_abi_to_filesystem,
        },
    }


def get_contract_abi(**query):
    backend_order = query.get('backend_order')
    if backend_order is None:
        backend_order = ['filesystem', 'download']
        query['backend_order'] = backend_order
    return backend_utils.run_on_backend(
        backend_functions=get_backend_functions()['get'], **query
    )


def save_contract_abi(contract_abi, **query):
    query['contract_abi'] = contract_abi
    return backend_utils.run_on_backend(
        backend_functions=get_backend_functions()['save'], **query
    )


def transfer_contract_abi(**kwargs):
    return backend_utils.transfer_backends(
        get=get_contract_abi, save=save_contract_abi, **kwargs
    )


def download_contract_abi(contract_address, name=None, **kwargs):

    common_kwargs = {'contract_address': contract_address}
    kwargs.setdefault('common_kwargs', {})
    kwargs['common_kwargs'] = dict(kwargs['common_kwargs'])
    kwargs['common_kwargs'].update(common_kwargs)

    save_kwargs = {'name': name}
    kwargs.setdefault('save_kwargs', {})
    kwargs['save_kwargs'] = dict(kwargs['save_kwargs'])
    kwargs['save_kwargs'].update(save_kwargs)

    return transfer_contract_abi(
        from_backend='etherscan', to_backend='filesystem', **kwargs
    )

