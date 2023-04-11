from __future__ import annotations

import typing

import toolsql

from ctc import config
from ctc import evm
from ctc import spec
from ... import management
from . import events_statements


async def async_intake_encoded_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent],
    query: spec.DBEventQuery,
    context: spec.Context,
    latest_block: int | None = None,
) -> None:

    import numpy as np

    if len(encoded_events) == 0:
        return

    # only insert blocks after a given number of confirmations
    if latest_block is None:
        latest_block = await evm.async_get_latest_block_number()
    required_confirmations = management.get_required_confirmations(
        context=context
    )
    latest_allowed_block = latest_block - required_confirmations
    if query['start_block'] > latest_allowed_block:
        return
    if query['end_block'] > latest_allowed_block:
        if isinstance(encoded_events[0], dict):
            blocks = np.array([event['block_number'] for event in encoded_events])
            confirmed_mask = blocks <= latest_allowed_block
            encoded_events = [
                event
                for event, confirmed in zip(encoded_events, confirmed_mask)
                if confirmed
            ]
        elif isinstance(encoded_events[0], tuple):
            encoded_events = [
                event
                for event in encoded_events
                if event[0] <= latest_allowed_block
            ]
        else:
            raise Exception()
        query = dict(query, end_block=latest_allowed_block)  # type: ignore

    # return early if no events to intake
    if len(encoded_events) == 0:
        return

    # insert into database
    db_config = config.get_context_db_config(
        schema_name='events',
        context=context,
    )
    async with toolsql.async_connect(db_config) as conn:
        await events_statements.async_upsert_event_query(
            event_query=query,
            conn=conn,
            context=context,
        )
        await events_statements.async_upsert_events(
            encoded_events=encoded_events,
            conn=conn,
            context=context,
        )

    return None

