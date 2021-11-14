from .. import event_utils


def get_erc20_transfers(
    token_address,
    start_block=None,
    end_block='latest',
    **event_kwargs
):
    return event_utils.get_events(
        contract_address=token_address,
        event_name='Transfer',
        start_block=start_block,
        end_block=end_block,
        **event_kwargs
    )

