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
    source='local',
) -> list[fourbyte_spec.Entry]:
    if source == 'local':
        return local_queries.query_function_signature(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
    elif source == 'remote':
        return await remote_queries.async_query_function_signature_remote(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
    else:
        raise Exception('unknown source: ' + str(source))


async def async_query_event_signature(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
    source='local',
) -> list[fourbyte_spec.Entry]:
    if source == 'local':
        return local_queries.query_event_signature(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
    elif source == 'remote':
        return await remote_queries.async_query_event_signature_remote(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
    else:
        raise Exception('unknown source: ' + str(source))

