from __future__ import annotations

import functools
from typing import Callable, Coroutine, Any, TypeVar

import sqlalchemy  # type: ignore
import toolsql

from ctc import spec
from . import connect_utils
from . import schema_utils


R = TypeVar('R')


def wrap_selector_with_connection(
    async_f: Callable[..., Coroutine[Any, Any, R | None]],
    schema_name: schema_utils.SchemaName
    | Callable[..., schema_utils.SchemaName | None],
    *,
    require_network: bool = True,
) -> Callable[..., Coroutine[Any, Any, R | None]]:

    # define new function
    @functools.wraps(async_f)
    async def async_connected_f(
        *args: Any,
        network: spec.NetworkReference | None = None,
        engine: toolsql.SAEngine | None = None,
        **kwargs: Any,
    ) -> R | None:
        # TODO: allow this function to accept a conn that already exists

        if network is None and require_network:
            raise Exception('must specify network')

        if not isinstance(schema_name, str) and hasattr(
            schema_name, '__call__'
        ):
            name = schema_name()
            if name is None:
                return None
        elif isinstance(schema_name, str):
            name = schema_name
        else:
            raise Exception('unknown schema_name format')

        # create engine
        if engine is None:
            engine = connect_utils.create_engine(
                schema_name=name,
                network=network,
            )

        # if cannot create engine, return None
        if engine is None:
            return None

        # connect and execute
        if require_network:
            kwargs['network'] = network
        try:
            with engine.connect() as conn:
                return await async_f(*args, conn=conn, **kwargs)
        except sqlalchemy.exc.OperationalError:
            return None

    return async_connected_f
