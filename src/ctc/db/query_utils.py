from __future__ import annotations

import functools
from typing import Callable, Coroutine, Any, TypeVar

from . import connect_utils
from . import schema_utils


R = TypeVar('R')


def with_connection(
    async_f: Callable[..., Coroutine[Any, Any, R | None]],
    schema_name: schema_utils.EVMSchemaName,
) -> Callable[..., Coroutine[Any, Any, R | None]]:

    # define new function
    @functools.wraps(async_f)
    async def async_connected_f(
        *args: Any,
        network: str,
        **kwargs: Any,
    ) -> R | None:

        # create engine
        engine = connect_utils.create_engine(
            schema_name=schema_name,
            network=network,
        )

        # if cannot create engine, return None
        if engine is None:
            return None

        # connect and execute
        with engine.connect() as conn:
            return await async_f(*args, conn=conn, **kwargs)

    return async_connected_f
