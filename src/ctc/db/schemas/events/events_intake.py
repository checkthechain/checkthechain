from __future__ import annotations

import typing

from ctc import evm
from ctc import spec
from ... import management
from . import events_statements


async def async_intake_encoded_events(
    *,
    encoded_events: typing.Sequence[spec.EncodedEvent],
    # encoded_events: spec.DataFrame,
    query: spec.EventQuery,
    network: spec.NetworkReference,
    latest_block: int | None = None,
) -> None:

    import sqlalchemy.exc  # type: ignore
    import numpy as np

    from ctc import db

    # only insert blocks after a given number of confirmations
    if latest_block is None:
        latest_block = await evm.async_get_latest_block_number()
    blocks = np.array([event['block_number'] for event in encoded_events])
    # blocks = encoded_events.index.get_level_values('block_number')
    required_confirmations = management.get_required_confirmations(network)
    if blocks[-1] > latest_block - required_confirmations:
        confirmed_mask = blocks <= latest_block - required_confirmations
        encoded_events = [
            event
            for event, confirmed in zip(encoded_events, confirmed_mask)
            if confirmed
        ]
        # encoded_events = encoded_events[confirmed_mask]

    engine = db.create_engine(schema_name='events', network=network)
    if engine is None:
        return None

    try:
        with engine.connect() as conn:
            await events_statements.async_upsert_event_query(
                query=query,
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
