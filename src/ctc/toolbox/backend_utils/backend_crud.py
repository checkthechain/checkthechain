from . import backend_exceptions


def get_backend_order(backend, backend_order):
    if backend_order is None and backend is None:
        backend_order = ['filesystem', 'node']
    elif backend is not None:
        backend_order = [backend]
    elif backend_order is not None:
        pass
    else:
        raise Exception('specify backend or backend_order')
    return backend_order


def run_on_backend(
    backend_functions, backend=None, backend_order=None, **function_kwargs
):
    backend_order = get_backend_order(backend, backend_order)
    for backend in backend_order:
        try:
            function = backend_functions.get(backend)
            return function(**function_kwargs)
        except backend_exceptions.DataNotFound:
            pass
    else:
        raise Exception('could not execute any of: ' + str(backend_functions))


async def async_run_on_backend(
    backend_functions, backend=None, backend_order=None, **function_kwargs
):
    backend_order = get_backend_order(backend, backend_order)
    for backend in backend_order:
        try:
            function = backend_functions.get(backend)
            return await function(**function_kwargs)
        except backend_exceptions.DataNotFound:
            pass
    else:
        raise Exception('could not execute any of: ' + str(backend_functions))


def transfer_backends(
    get,
    save,
    from_backend,
    to_backend,
    get_kwargs=None,
    save_kwargs=None,
    common_kwargs=None,
    **more_common_kwargs
):
    if common_kwargs is None:
        common_kwargs = {}
    common_kwargs = dict(common_kwargs, **more_common_kwargs)

    if get_kwargs is None:
        get_kwargs = {}
    get_kwargs = dict(common_kwargs, **get_kwargs)
    result = get(backend=from_backend, **get_kwargs)

    if save_kwargs is None:
        save_kwargs = {}
    save_kwargs = dict(common_kwargs, **get_kwargs)

    return save(result, backend=to_backend, **save_kwargs)


async def async_transfer_backends(
    get,
    save,
    from_backend,
    to_backend,
    get_kwargs=None,
    save_kwargs=None,
    common_kwargs=None,
    **more_common_kwargs
):
    if common_kwargs is None:
        common_kwargs = {}
    common_kwargs = dict(common_kwargs, **more_common_kwargs)

    if get_kwargs is None:
        get_kwargs = {}
    get_kwargs = dict(common_kwargs, **get_kwargs)
    result = await get(backend=from_backend, **get_kwargs)

    if save_kwargs is None:
        save_kwargs = {}
    save_kwargs = dict(common_kwargs, **get_kwargs)

    return await save(result, backend=to_backend, **save_kwargs)

