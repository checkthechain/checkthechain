import toolstr
import tooltime

from ctc import binary
from ctc import evm
from ctc import rpc
from ctc import spec
from .. import block_utils


async def async_print_transaction_summary(transaction_hash, sort_logs_by=None):
    transaction = await rpc.async_eth_get_transaction_by_hash(transaction_hash)
    transaction_receipt = await rpc.async_eth_get_transaction_receipt(
        transaction_hash=transaction_hash
    )
    block = await block_utils.async_get_block(
        transaction['block_number'], include_full_transactions=False
    )

    from ctc.protocols import chainlink_utils

    eth_usd = await chainlink_utils.async_get_eth_price(
        block=transaction['block_number']
    )

    print('Transaction')
    print('-----------')
    print('- hash:', transaction['hash'])
    print('- from:', transaction['from'])
    print('- to:', transaction['to'])
    print()
    print()
    print('Receipt')
    print('-------')
    print('- success:', bool(transaction_receipt['status']))
    print('- time:', block['timestamp'])
    print('- timestamp:', tooltime.timestamp_to_iso(block['timestamp']))
    print('- block number:', transaction['block_number'])
    print(
        '- transaction index:',
        transaction_receipt['transaction_index'],
        '/',
        len(block['transactions']),
    )
    print(
        '- gas used:',
        toolstr.format(transaction_receipt['gas_used']),
        '/',
        toolstr.format(transaction['gas']),
    )
    print('- gas price:', toolstr.format(transaction['gas_price'] / 1e9))
    if 'max_priority_fee_per_gas' in transaction:
        print(
            '- priority + base:',
            toolstr.format(transaction['max_priority_fee_per_gas'] / 1e9),
            '+',
            toolstr.format(block['base_fee_per_gas'] / 1e9),
        )
    fee = transaction_receipt['gas_used'] * transaction['gas_price'] / 1e18
    fee_usd = fee * eth_usd
    print(
        '- total fee:',
        toolstr.format(fee),
        'ETH',
        '($' + toolstr.format(fee_usd) + ')',
    )

    if transaction['input'] == '0x':
        print()
        print()
        print('Call Data')
        print('---------')
        print('[none]')
    else:
        try:
            contract_abi = await evm.async_get_contract_abi(
                contract_address=transaction['to']
            )
        except spec.AbiNotFoundException:
            print()
            print()
            print('No Contract ABI Available')
            print('-------------------------')
            return

        function_abi = await evm.async_get_function_abi(
            contract_address=transaction['to'],
            function_selector=transaction['input'][:10],
        )
        call_data = binary.decode_call_data(
            call_data=transaction['input'],
            function_abi=function_abi,
        )
        print()
        print()
        print('Call Data')
        print('---------')
        print(
            call_data['function_selector'],
            '-->',
            binary.get_function_signature(function_abi=function_abi),
        )
        for p, (name, value) in enumerate(call_data['named_parameters'].items()):
            if (
                value
                == 115792089237316195423570985008687907853269984665640564039457584007913129639935
            ):
                value = 'INT_MAX'
            print('    ' + str(p + 1) + '.', name, '=', value)

    print()
    print()
    print('Logs')
    print('----')
    logs = transaction_receipt['logs']
    if len(logs) == 0:
        print('[none]')

    else:
        # if sort_logs_by == 'signature':
        #     logs = sorted(
        #         logs,
        #         key=lambda log: binary.get_event_signature(
        #             contract_address=log['address'],
        #             event_hash=log['topics'][0],
        #         ),
        #     )
        for l, log in enumerate(logs):
            if l != 0:
                print()

            event_abi = await evm.async_get_event_abi(
                contract_address=log['address'],
                event_hash=log['topics'][0],
            )
            normalized_event = binary.normalize_event(
                event=log,
                arg_prefix=None,
                event_abi=event_abi,
            )
            event_signature = binary.get_event_signature(event_abi=event_abi)
            print(event_signature, '-->', log['address'])
            for e, (name, value) in enumerate(normalized_event['args'].items()):
                if (
                    value
                    == 115792089237316195423570985008687907853269984665640564039457584007913129639935
                ):
                    value = 'INT_MAX'

                # not sure if this is what should be done
                if isinstance(value, bytes):
                    value = binary.convert(value, 'prefix_hex')

                print('    ' + str(e + 1) + '.', name, '=', value)

