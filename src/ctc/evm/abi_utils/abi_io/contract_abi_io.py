import typing

from ctc import rpc
from ctc import spec
from ctc.toolbox import backend_utils

from ... import address_utils
from . import contract_abi_backends


def get_backend_functions():
    return {
        'get': {
            'filesystem': contract_abi_backends.async_get_contract_abi_from_filesystem,
            'download': async_download_contract_abi,
            'etherscan': contract_abi_backends.async_get_contract_abi_from_etherscan,
        },
        'save': {
            'filesystem': contract_abi_backends.async_save_contract_abi_to_filesystem,
        },
    }


async def async_get_contract_abi(**query):
    backend_order = query.get('backend_order')
    if backend_order is None:
        backend_order = ['filesystem', 'download']
        query['backend_order'] = backend_order
    return await backend_utils.async_run_on_backend(
        backend_functions=get_backend_functions()['get'], **query
    )


async def async_save_contract_abi(contract_abi, **query):
    query['contract_abi'] = contract_abi
    return await backend_utils.async_run_on_backend(
        backend_functions=get_backend_functions()['save'], **query
    )


async def async_transfer_contract_abi(**kwargs):
    return await backend_utils.async_transfer_backends(
        get=async_get_contract_abi, save=async_save_contract_abi, **kwargs
    )


async def async_download_contract_abi(
    contract_address,
    name=None,
    provider: spec.ProviderSpec = None,
    **kwargs
):

    provider = rpc.get_provider(provider)
    network = provider['network']
    if network is None:
        raise Exception('could not determine network')

    common_kwargs = {'contract_address': contract_address, 'network': network}
    kwargs.setdefault('common_kwargs', {})
    kwargs['common_kwargs'] = dict(kwargs['common_kwargs'])
    kwargs['common_kwargs'].update(common_kwargs)

    save_kwargs = {'name': name, 'network': network}
    kwargs.setdefault('save_kwargs', {})
    kwargs['save_kwargs'] = dict(kwargs['save_kwargs'])
    kwargs['save_kwargs'].update(save_kwargs)

    contract_abi = await async_transfer_contract_abi(
        from_backend='etherscan', to_backend='filesystem', **kwargs
    )

    try:
        await address_utils.async_save_eip897_abi(
            contract_address=contract_address, provider=provider,
        )
        contract_abi = (
            await contract_abi_backends.async_get_contract_abi_from_filesystem(
                contract_address=contract_address, network=network,
            )
        )
    except Exception:
        pass

    return contract_abi

