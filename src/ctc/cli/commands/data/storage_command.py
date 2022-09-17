from __future__ import annotations

import toolcli

from ctc import evm
from ctc import rpc
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_storage_command,
        'help': 'get value of storage slot',
        'args': [
            {'name': 'contract_address', 'help': 'address of contract'},
            {'name': 'slot', 'help': 'address of storage slot'},
            {'name': '--block', 'help': 'block number'},
            {
                'name': '--type',
                'help': 'decode data using this datatype',
                'dest': 'datatype',
            },
        ],
        'examples': [
            '0x245cc372c84b3645bf0ffe6538620b04a217988b 0x0',
            '0x245cc372c84b3645bf0ffe6538620b04a217988b 0x0 --type address',
            '0x245cc372c84b3645bf0ffe6538620b04a217988b 0x0 --block 14000000',
        ],
    }


async def async_storage_command(
    *,
    contract_address: str,
    slot: str,
    block: spec.BlockNumberReference | None,
    datatype: str | None,
) -> None:

    contract_address = await evm.async_resolve_address(
        contract_address,
        block=block,
    )

    result = await rpc.async_eth_get_storage_at(
        contract_address,
        position=slot,
        block_number=block,
    )
    if datatype is None:
        print(result)
    else:
        as_bytes = evm.binary_convert(result, 'binary')
        decoded = evm.abi_decode(as_bytes, datatype)
        print(decoded)
