from __future__ import annotations

import typing

from .. import fourbyte_db
from .. import fourbyte_spec
from . import local_queries
from . import remote_queries


async def async_query_function_signatures(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
    use_local: bool = True,
    use_remote: bool = True,
) -> typing.Sequence[fourbyte_spec.Entry]:

    if not use_local and not use_remote:
        raise Exception('should use at least one of use_local or use_remote')

    if use_local:
        result = await local_queries.async_query_local_function_signatures(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
        if result is not None and len(result) > 0:
            return result

    if use_remote:
        result = await remote_queries.async_query_remote_function_signatures(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )

        # type ignoring because of mypy bug
        await fourbyte_db.async_intake_function_signatures(
            typing.cast(typing.Sequence[fourbyte_spec.PartialEntry], result)  # type: ignore
        )

        return result

    return []


async def async_query_event_signatures(
    hex_signature: typing.Optional[str] = None,
    *,
    id: typing.Optional[int] = None,
    bytes_signature: typing.Optional[str] = None,
    text_signature: typing.Optional[str] = None,
    use_local: bool = True,
    use_remote: bool = True,
) -> typing.Sequence[fourbyte_spec.Entry]:

    if not use_local and not use_remote:
        raise Exception('should use at least one of use_local or use_remote')

    if use_local:
        result = await local_queries.async_query_local_event_signatures(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )
        if result is not None and len(result) > 0:
            return result

    if use_remote:
        result = await remote_queries.async_query_remote_event_signatures(
            id=id,
            bytes_signature=bytes_signature,
            hex_signature=hex_signature,
            text_signature=text_signature,
        )

        # type ignoring because of mypy bug
        await fourbyte_db.async_intake_event_signatures(
            typing.cast(typing.Sequence[fourbyte_spec.PartialEntry], result)  # type: ignore
        )

        return result

    return []
