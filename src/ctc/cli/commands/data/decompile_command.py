"""
TODO:
- add grouping for specific groups:
        - erc20 functions and events
        - proxy functions
        - erc721 erc1155
    - could group these either spatially or by color
- add listing of unknown signatures
- add event signatures
"""

from ctc import evm
from ctc import rpc


def get_command_spec():
    return {
        'f': async_decompile_command,
        'help': 'decompile contract abi',
        'args': [
            {
                'name': 'address_or_bytecode',
                'help': 'contract address or hex bytecode',
            },
        ],
    }


async def async_decompile_command(address_or_bytecode):
    if len(address_or_bytecode) == 42:
        bytecode = await rpc.async_eth_get_code(address_or_bytecode)
    else:
        bytecode = address_or_bytecode

    decompiled_function_abis = await evm.async_decompile_function_abis(
        bytecode,
        sort='text_signature',
    )

    for entry in decompiled_function_abis:
        print(entry['hex_signature'], entry['text_signature'])

    await rpc.async_close_http_session()

