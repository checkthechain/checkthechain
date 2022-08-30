"""this code is fragile and hacky, it needs to get replaced in future"""
from __future__ import annotations

import typing

from . import backend_exceptions

if typing.TYPE_CHECKING:
    T = typing.TypeVar('T')


def get_backend_order(
    backend: str | None = None,
    backend_order: typing.Sequence[str] | None = None,
) -> typing.Sequence[str]:
    if backend_order is None and backend is None:
        return ['filesystem', 'node']
    elif backend is not None:
        return [backend]
    elif backend_order is not None:
        return backend_order
    else:
        raise Exception('specify backend or backend_order')


def run_on_backend(
    backend_functions: typing.Mapping[str, typing.Callable[..., T]],
    backend: str | None = None,
    *,
    backend_order: typing.Sequence[str] | None = None,
    **function_kwargs: typing.Any,
) -> T:
    backend_order = get_backend_order(backend, backend_order)
    for backend in backend_order:
        try:
            function = backend_functions.get(backend)
            if function is None:
                raise Exception('unknown backend: ' + str(backend))
            return function(**function_kwargs)
        except backend_exceptions.DataNotFound:
            pass
    else:
        raise Exception('could not execute any of: ' + str(backend_functions))


async def async_run_on_backend(
    backend_functions: typing.Mapping[
        str, typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, T]]
    ],
    backend: str | None = None,
    *,
    backend_order: typing.Sequence[str] | None = None,
    **function_kwargs: typing.Any,
) -> T:
    backend_order = get_backend_order(backend, backend_order)
    for backend in backend_order:
        try:
            function = backend_functions.get(backend)
            if function is None:
                raise Exception('unknown backend: ' + str(backend))
            return await function(**function_kwargs)
        except backend_exceptions.DataNotFound:
            pass
    else:
        raise Exception('could not execute any of: ' + str(backend_functions))


def transfer_backends(
    get: typing.Callable[..., typing.Any],
    save: typing.Callable[..., typing.Any],
    *,
    from_backend: str,
    to_backend: str,
    get_kwargs: typing.Mapping[str, typing.Any] | None = None,
    save_kwargs: typing.Mapping[str, typing.Any] | None = None,
    common_kwargs: typing.Mapping[str, typing.Any] | None = None,
    **more_common_kwargs: typing.Any,
) -> typing.Any:
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
    get: typing.Callable[..., typing.Any],
    save: typing.Callable[..., typing.Any],
    *,
    from_backend: str,
    to_backend: str,
    get_kwargs: typing.Mapping[str, typing.Any] | None = None,
    save_kwargs: typing.Mapping[str, typing.Any] | None = None,
    common_kwargs: typing.Mapping[str, typing.Any] | None = None,
    **more_common_kwargs: typing.Any,
) -> typing.Any:
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
