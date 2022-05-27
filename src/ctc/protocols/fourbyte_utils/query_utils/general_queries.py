from __future__ import annotations

import typing

from .. import fourbyte_spec
from . import local_queries
from . import remote_queries


async def async_query_function_signature(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
    use_local: bool = True,
    use_remote: bool = True,
) -> list[fourbyte_spec.Entry]:

    if not use_local and not use_remote:
        raise Exception('should use at least one of use_local or use_remote')

    if use_local:
        result = local_queries.query_function_signature(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
        if len(result) > 0:
            return result

    if use_remote:
        return await remote_queries.async_query_function_signature_remote(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )

    return []


async def async_query_event_signature(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
    use_local: bool = True,
    use_remote: bool = True,
) -> list[fourbyte_spec.Entry]:

    if not use_local and not use_remote:
        raise Exception('should use at least one of use_local or use_remote')

    if use_local:
        result = local_queries.query_event_signature(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
        if len(result) > 0:
            return result

    if use_remote:
        return await remote_queries.async_query_event_signature_remote(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )

    return []
