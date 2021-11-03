
def fetch_token_transfers(
    token_address,
    abi=None,
    start_block=None,
    end_block='latest',
    blocks_per_chunk=2000,
    parallel_kwargs={'n_workers': 60},
):
    raise NotImplementedError('reimplement with event_utils')

    # # should just hardcode the Transfer abi entry here
    # if abi is None:
    #     abi = code.fetch_abi(token_address)

    # token_transfers = web3_utils.fetch_events_as_chunks(
    #     contract_address=token_address,
    #     contract_name=None,
    #     contract_abi=abi,
    #     event_name='Transfer',
    #     start_block=start_block,
    #     end_block=end_block,
    #     blocks_per_chunk=blocks_per_chunk,
    #     parallel_kwargs=parallel_kwargs,
    # )

    # return token_transfers

