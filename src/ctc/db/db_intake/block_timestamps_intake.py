from ctc import rpc
from .. import db_crud
from .. import db_management
from .. import connect_utils


async def async_intake_block(block, provider=None):

    # determine whether to store block
    network = rpc.get_provider_network(provider=provider)
    min_confirmations = db_management.get_min_confirmations(
        datatype='block_timestamps',
        network=network,
    )
    engine = connect_utils.create_engine(
        datatype='block_timestamps',
        network=network,
    )
    check_if_exists = False
    with engine.connect() as conn:
        if (
            check_if_exists
            and db_crud.get_block_timestamp(
                conn=conn, block_number=block['number']
            )
            is not None
        ):
            store = False
        else:
            max_block = db_crud.get_max_block_number(conn=conn, network=network)
            if block['number'] <= max_block - min_confirmations:
                store = True
            else:
                latest_block = await rpc.async_eth_block_number(
                    provider=provider,
                )
                store = block['number'] <= latest_block - min_confirmations

    # store data in db
    if store:
        with engine.begin() as conn:
            db_crud.set_block_timestamp(
                conn=conn,
                block_number=block['number'],
                timestamp=block['timestamp'],
            )


async def async_intake_blocks(blocks, provider=None):
    """

    TODO: database should store a max_complete_block number
    - indicates that ALL blocks below this height are stored
    - enables not re-storing anything below this height upon intake
    """

    # determine whether to store block
    network = rpc.get_provider_network(provider=provider)
    min_confirmations = db_management.get_min_confirmations(
        datatype='block_timestamps',
        network=network,
    )
    engine = connect_utils.create_engine(
        datatype='block_timestamps',
        network=network,
    )
    with engine.connect() as conn:
        max_intake_block = max(block['number'] for block in blocks)
        max_stored_block = db_crud.get_max_block_number(conn=conn, network=network)
        if max_intake_block <= max_stored_block - min_confirmations:
            store_blocks = blocks
        else:
            latest_block = await rpc.async_eth_block_number(
                provider=provider,
            )
            store_blocks = [
                block
                for block in blocks
                if block['number'] <= latest_block - min_confirmations
            ]

    # store data in db
    if len(store_blocks) > 0:
        blocks_timestamps = {
            block['number']: block['timestamp']
            for block in store_blocks
        }
        with engine.begin() as conn:
            db_crud.set_blocks_timestamps(
                conn=conn,
                blocks_timestamps=blocks_timestamps,
            )

