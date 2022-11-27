from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ... import management
from . import events_statements


async def async_intake_encoded_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent] | spec.DataFrame,
    # encoded_events: spec.DataFrame,
    query: spec.DBEventQuery,
    network: spec.NetworkReference,
    latest_block: int | None = None,
) -> None:

    import sqlalchemy.exc  # type: ignore
    import numpy as np
    from ctc import db

    if spec.is_dataframe(encoded_events):
        encoded_events = encoded_events.reset_index().to_dict(orient='records')  # type: ignore

    # only insert blocks after a given number of confirmations
    if latest_block is None:
        latest_block = await evm.async_get_latest_block_number()
    blocks = np.array([event['block_number'] for event in encoded_events])
    required_confirmations = management.get_required_confirmations(network)
    latest_allowed_block = latest_block - required_confirmations
    if query['start_block'] > latest_allowed_block:
        return
    if query['end_block'] > latest_allowed_block:
        if len(blocks) > 0:
            confirmed_mask = blocks <= latest_allowed_block
            encoded_events = [
                event
                for event, confirmed in zip(encoded_events, confirmed_mask)
                if confirmed
            ]
        query['end_block'] = latest_allowed_block

    engine = db.create_engine(schema_name='events', network=network)
    if engine is None:
        return None

    try:
        with engine.begin() as conn:

            await events_statements.async_upsert_event_query(
                event_query=query,
                conn=conn,
                network=network,
            )
            await events_statements.async_upsert_events(
                encoded_events=encoded_events,
                conn=conn,
                network=network,
            )
    except sqlalchemy.exc.OperationalError:
        pass

    return None
