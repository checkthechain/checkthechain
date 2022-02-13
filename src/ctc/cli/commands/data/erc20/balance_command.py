import toolstr

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_balance_command,
        'args': [
            {'name': 'erc20_address'},
            {'name': 'wallet_address'},
            {'name': '--block'},
            {'name': '--raw', 'kwargs': {'action': 'store_true'}},
        ],
    }


async def async_balance_command(erc20_address, wallet_address, block, raw):
    balance = await evm.async_get_erc20_balance_of(
        address=wallet_address,
        token=erc20_address,
        block=block,
        normalize=(not raw),
    )
    if raw:
        print(balance)
    else:
        print(toolstr.format(balance))
    await rpc.async_close_http_session()

