from __future__ import annotations

import functools
from typing import Callable, Coroutine, Any, TypeVar

import toolsql

from ctc import spec
from . import connect_utils


R = TypeVar('R')


def wrap_selector_with_connection(
    async_f: Callable[..., Coroutine[Any, Any, R | None]],
    schema_name: spec.SchemaName | Callable[..., spec.SchemaName | None],
) -> Callable[..., Coroutine[Any, Any, R | None]]:

    # define new function
    @functools.wraps(async_f)
    async def async_connected_f(
        *args: Any,
        context: spec.Context,
        db_config: toolsql.DBConfig | None = None,
        raise_if_cannot_connect: bool = False,
        raise_if_table_dne: bool = False,
        **kwargs: Any,
    ) -> R | None:

        # determine schema_name
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

        # try to query data
        try:
            async with connect_utils.async_connect(
                context=context,
                db_config=db_config,
                schema=name,
                read_only=True,
            ) as conn:
                return await async_f(*args, conn=conn, context=context, **kwargs)

        # handle errors, either by returning None or raising exceptions
        except toolsql.CannotConnect as e:
            if raise_if_cannot_connect:
                raise e
            else:
                return None
        except toolsql.TableDoesNotExist as e:
            if raise_if_table_dne:
                raise e
            else:
                return None

    # return decorated function
    return async_connected_f

