from __future__ import annotations

from ctc import evm
from ctc import spec

from .. import abi_utils
from . import address_data


async def async_print_address_summary(
    address: spec.Address,
    *,
    verbose: bool | int = False,
    max_width: int = 80,
    provider: spec.ProviderReference = None,
    raw: bool = False,
) -> None:
    """print summary of address

    TODO (with more data)
    - transactions
    - transfers
    """

    import asyncio
    import toolstr
    import tooltime
    from ctc import cli
    from ctc import rpc

    styles = cli.get_cli_styles()

    eth_balance_coroutine = evm.async_get_eth_balance(
        address, provider=provider
    )
    transaction_count_coroutine = rpc.async_eth_get_transaction_count(
        address, provider=provider
    )

    # contract data
    code_coroutine = rpc.async_eth_get_code(address, provider=provider)

    [eth_balance, transaction_count, code] = await asyncio.gather(
        eth_balance_coroutine,
        transaction_count_coroutine,
        code_coroutine,
    )

    is_contract = code != '0x'
    if is_contract:
        address_type = 'contract'
    else:
        address_type = 'EOA'

    title = 'Address ' + address.lower()
    toolstr.print_text_box(title, style=styles['title'])
    rows = [
        ('checksum', toolstr.add_style(address_data.get_address_checksum(address), styles['metavar'])),
        ('address type', address_type),
        ('ETH balance', eth_balance),
        ('transaction count', transaction_count),
    ]
    print()
    toolstr.print_table(
        rows,
        border=styles['comment'],
        column_justify=['right', 'left'],
        column_styles=[styles['option'], styles['description']],
    )

    if verbose:
        creation_block = await evm.async_get_contract_creation_block(address)
        if creation_block is not None:
            block_timestamp = await evm.async_get_block_timestamp(
                creation_block
            )
            age = tooltime.get_age(block_timestamp, 'TimelengthPhrase')
            print('- creation block:', creation_block)
            print('- age:', age)

    if is_contract:

        is_erc20 = await evm.async_is_erc20(address)

        if is_erc20:
            print()
            print()
            await evm.async_print_erc20_summary(address, include_address=False)

        provider = rpc.get_provider(provider)
        network = provider['network']
        contract_abi = await abi_utils.async_get_contract_abi(
            contract_address=address,
            network=network,
        )

        print()
        print()
        if raw:
            import json
            import toolstr

            toolstr.print_header('Raw JSON ABI')
            as_str = json.dumps(contract_abi, sort_keys=True, indent=4)
            print(as_str)
        else:
            abi_utils.print_contract_abi(
                contract_abi=contract_abi,
                max_width=max_width,
                verbose=verbose,
            )
