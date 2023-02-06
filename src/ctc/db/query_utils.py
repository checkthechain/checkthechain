from __future__ import annotations

import functools
from typing import Callable, Coroutine, Any, TypeVar

import toolsql

from ctc import config
from ctc import spec


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

        # connect and execute
        db_config = config.get_context_db_config(
            schema_name=name,
            context=context,
        )
        try:
            async with toolsql.async_connect(db_config) as conn:
                return await async_f(
                    *args, conn=conn, context=context, **kwargs
                )
        except Exception:
            print("COULD NOT CONNECT TO DATABASE")
            return None

    return async_connected_f

