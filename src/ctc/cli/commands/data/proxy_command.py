from __future__ import annotations

import typing

import toolcli
import toolstr

from ctc import evm
from ctc.evm.address_utils import proxy_utils
from ctc import spec


def get_command_spec() -> toolcli.CommandSpec:
    return {
        'f': async_proxy_command,
        'help': 'print proxy information about contract',
        'args': [
            {'name': 'contract_address', 'help': 'address to get proxy of'},
            {
                'name': ['--verbose', '-v'],
                'help': 'print additional information',
                'action': 'store_true',
            },
            {'name': '--block', 'help': 'block to query', 'default': 'latest'},
        ],
        'examples': [
            '0xee6a57ec80ea46401049e92587e52f5ec1c24785',  # EIP1967
        ],
    }


async def async_proxy_command(
    contract_address: spec.Address,
    verbose: bool,
    block: spec.BlockNumberReference,
) -> None:

    if verbose:
        eip_1967_address = (
            await proxy_utils._async_get_eip1967_proxy_logic_address(
                contract_address,
                block=block,
            )
        )
        uses_eip_1967 = (
            eip_1967_address != '0x0000000000000000000000000000000000000000'
        )

        try:
            eip_897_address = (
                await proxy_utils._async_get_eip897_implementation(
                    contract_address,
                    block=block,
                )
            )
            uses_eip_897 = True
        except spec.exceptions.rpc_exceptions.RpcException:
            eip_897_address = None
            uses_eip_897 = False

        if eip_897_address is not None and eip_1967_address != eip_897_address:
            print('EIP-897 and EIP-1967 both used, but addresses do not match')
            return

        if uses_eip_897:
            proxy_address = eip_897_address
        elif uses_eip_1967:
            proxy_address = eip_1967_address

        toolstr.print_text_box('Proxy Summary for ' + str(contract_address))
        rows: typing.Sequence[typing.Sequence[typing.Any]] = [
            ['block', block],
            ['uses EIP-897', uses_eip_897],
            ['uses EIP-1967', uses_eip_1967],
            ['contract_address', contract_address],
            ['proxy_address', proxy_address],
        ]
        toolstr.print_table(rows, column_justify=['right', 'left'], compact=2)

    else:
        proxy_address = await evm.async_get_proxy_address(contract_address)
        print(proxy_address)
