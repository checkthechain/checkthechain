from __future__ import annotations

import time

from ctc import evm
from ctc import spec
from .. import binary_utils
from .. import block_utils
from . import transaction_types


async def async_print_transaction_summary(
    transaction_hash: str,
    sort_logs_by: str | None = None,
) -> None:
    """print summary of transaction"""

    import asyncio
    import toolstr
    import tooltime
    from ctc import cli
    from ctc import rpc
    from ctc.protocols import chainlink_utils

    transaction_coroutine = rpc.async_eth_get_transaction_by_hash(
        transaction_hash
    )
    transaction_receipt_task = asyncio.create_task(
        rpc.async_eth_get_transaction_receipt(transaction_hash=transaction_hash)
    )

    transaction = await transaction_coroutine
    block_task = asyncio.create_task(
        block_utils.async_get_block(
            transaction['block_number'], include_full_transactions=False
        )
    )
    eth_usd_task = asyncio.create_task(
        chainlink_utils.async_get_eth_price(block=transaction['block_number'])
    )

    styles = cli.get_cli_styles()
    toolstr.print_text_box('Transaction Summary', style=styles['title'])
    cli.print_bullet(key='hash', value=transaction['hash'])
    cli.print_bullet(key='from', value=transaction['from'])
    cli.print_bullet(key='to', value=transaction['to'])
    cli.print_bullet(key='block number', value=transaction['block_number'])
    cli.print_bullet(
        key='transaction index', value=transaction['transaction_index']
    )
    cli.print_bullet(key='nonce', value=transaction['nonce'])

    type = transaction_types.get_transaction_type(transaction)
    type_name = transaction_types.get_transaction_type_name(type)
    type_str = type_name + ' (' + str(type) + ')'
    cli.print_bullet(key='type', value=type_str)

    cli.print_bullet(key='call data length', value=len(transaction['input']))

    block, eth_usd = await asyncio.gather(block_task, eth_usd_task)
    timestamp = block['timestamp']
    cli.print_bullet(key='timestamp', value=timestamp)
    cli.print_bullet(key='time', value=tooltime.timestamp_to_iso(timestamp))
    age = int(time.time()) - timestamp
    cli.print_bullet(key='age', value=tooltime.timelength_to_phrase(age))
    print()
    print()
    transaction_receipt = await transaction_receipt_task
    toolstr.print_text_box('Transaction Receipt', style=styles['title'])
    cli.print_bullet(key='success', value=bool(transaction_receipt['status']))
    cli.print_bullet(
        key='transaction index',
        value=str(transaction_receipt['transaction_index'])
        + ' / '
        + str(len(block['transactions'])),
    )
    cli.print_bullet(
        key='gas used',
        value=toolstr.format(transaction_receipt['gas_used'])
        + ' / '
        + toolstr.format(transaction['gas']),
    )
    cli.print_bullet(
        key='gas price',
        value=toolstr.format(transaction['gas_price'] / 1e9) + ' gwei',
    )
    if 'max_priority_fee_per_gas' in transaction:
        base_fee_per_gas = block.get('base_fee_per_gas')
        if base_fee_per_gas is None:
            base_fee_per_gas = 0
        cli.print_bullet(
            key='priority + base',
            value=toolstr.format(transaction['max_priority_fee_per_gas'] / 1e9)
            + ' + '
            + toolstr.format(int(base_fee_per_gas) / 1e9)
            + ' gwei',
        )
    fee = transaction_receipt['gas_used'] * transaction['gas_price'] / 1e18
    fee_usd = fee * eth_usd
    cli.print_bullet(
        key='total fee',
        value=toolstr.format(fee) + ' ETH ($' + toolstr.format(fee_usd) + ')',
    )

    if transaction['input'] == '0x':
        print()
        print()
        toolstr.print_text_box('Call Data', style=styles['title'])
        print('[none]')
    else:
        try:
            contract_abi_task = asyncio.create_task(
                evm.async_get_contract_abi(
                    contract_address=transaction['to'],
                    verbose=False,
                )
            )
            contract_abi = await contract_abi_task
        except spec.AbiNotFoundException:
            print()
            print()
            print('[no contract ABI available]')
            return

        try:
            function_abi = await evm.async_get_function_abi(
                contract_address=transaction['to'],
                function_selector=transaction['input'][:10],
            )
        except Exception:
            print()
            print()
            print('could not find function ABI. custom proxy being used?')
            return

        call_data = evm.decode_call_data(
            call_data=transaction['input'],
            function_abi=function_abi,
        )
        print()
        print()

        from ctc.cli.commands.compute import decode_call_command

        await decode_call_command.async_decode_call_command(
            args=[transaction_hash],
            title='Call Data',
        )

    print()
    print()
    toolstr.print_text_box('Logs', style=styles['title'])
    logs = transaction_receipt['logs']
    if len(logs) == 0:
        print('[none]')

    else:
        # if sort_logs_by == 'signature':
        #     logs = sorted(
        #         logs,
        #         key=lambda log: binary_utils.get_event_signature(
        #             contract_address=log['address'],
        #             event_hash=log['topics'][0],
        #         ),
        #     )
        for li, log in enumerate(logs):
            if li != 0:
                print()

            event_abi = await evm.async_get_event_abi(
                contract_address=log['address'],
                event_hash=log['topics'][0],
            )
            normalized_event = evm.normalize_event(
                event=log,
                arg_prefix=None,
                event_abi=event_abi,
            )
            # event_signature = binary_utils.get_event_signature(event_abi=event_abi)
            stylized_event_signature = (
                toolstr.add_style(event_abi['name'], styles['option'])
                + toolstr.add_style('(', styles['title'])
                + toolstr.add_style(',', styles['title']).join(
                    toolstr.add_style(item['type'], styles['option'])
                    for item in event_abi['inputs']
                )
                + toolstr.add_style(')', styles['title'])
            )
            toolstr.print(
                stylized_event_signature,
                toolstr.add_style('-->', styles['comment']),
                toolstr.add_style(log['address'], styles['metavar']),
                style=styles['description'] + ' bold',
            )
            for e, (name, value) in enumerate(normalized_event['args'].items()):
                if (
                    value
                    == 115792089237316195423570985008687907853269984665640564039457584007913129639935
                ):
                    value = 'INT_MAX'

                # not sure if this is what should be done
                if isinstance(value, bytes):
                    value = binary_utils.binary_convert(value, 'prefix_hex')

                cli.print_bullet(
                    key=name,
                    value=value,
                    colon_str=' = ',
                    number=e + 1,
                    indent=4,
                )
