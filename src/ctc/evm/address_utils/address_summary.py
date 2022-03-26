from __future__ import annotations

import json
import typing

import toolstr

from ctc import evm
from ctc import rpc
from ctc import spec

from .. import abi_utils
from . import address_data


async def async_print_address_summary(
    address: spec.Address,
    verbose: typing.Union[bool, int] = 0,
    max_width: int = 80,
    provider: spec.ProviderSpec = None,
    raw: bool = False,
) -> None:
    """

    TODO (with more data)
    - transactions
    - transfers
    """

    eth_balance = await evm.async_get_eth_balance(address, provider=provider)
    transaction_count = await rpc.async_eth_get_transaction_count(
        address, provider=provider
    )

    # contract data
    code = await rpc.async_eth_get_code(address, provider=provider)
    is_contract = code != '0x'
    if is_contract:
        address_type = 'contract'
    else:
        address_type = 'EOA'

    title = 'Address ' + address.lower()
    print(title)
    print('─' * len(title))
    print('- checksum:', address_data.get_address_checksum(address))
    print('- address type:', address_type)
    print('- ETH balance:', eth_balance)
    print('- transaction count:', transaction_count)

    if is_contract:
        print()
        print()

        provider = rpc.get_provider(provider)
        network = provider['network']
        contract_abi = await abi_utils.async_get_contract_abi(
            contract_address=address,
            network=network,
        )

        if raw:
            toolstr.print_header('Raw JSON ABI')
            as_str = json.dumps(contract_abi, sort_keys=True, indent=4)
            print(as_str)
        else:
            abi_utils.print_contract_abi_human_readable(
                contract_abi=contract_abi,
                max_width=max_width,
                verbose=verbose,
            )

